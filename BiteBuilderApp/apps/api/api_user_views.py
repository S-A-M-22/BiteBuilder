# apps/api/api_user_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import os, random, time, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.utils import timezone
from datetime import datetime, timedelta
import bcrypt
from django.views.decorators.csrf import ensure_csrf_cookie
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)

from ..users.views import (
    _sb_public,
    _sb_service,
    _start_login_session,
)
from ..users.models import Profile

# ========== Input Validation Functions ==========
def validate_string_length(value, max_length=255, field_name="Field"):
    """Validate string length to prevent massive inputs"""
    if value and len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")
    return value

def validate_username(username):
    """Validate username format: 3-32 characters, alphanumeric and underscore only"""
    if not username or len(username) < 3 or len(username) > 32:
        raise ValidationError("Username must be 3-32 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")
    return username

def validate_otp_code(code):
    """Validate OTP code: must be exactly 6 digits"""
    if not code or not re.match(r'^\d{6}$', code):
        raise ValidationError("Invalid OTP code format")
    return code

def validate_password_length(password):
    """Validate password length"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValidationError("Password is too long")
    return password

@api_view(["POST"])
def api_register(request):
    data = request.data
    
    try:
        # Validate and sanitize inputs
        username = validate_string_length(data.get("username", "").strip(), 32, "Username")
        validate_username(username)
        
        email = validate_string_length(data.get("email", "").strip(), 255, "Email")
        validate_email(email)
        
        password = data.get("password", "").strip()
        validate_password_length(password)
        
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)

    if not username or not email or not password:
        return Response({"error": "Missing fields"}, status=400)

    try:
        svc = _sb_service()

        # 🔍 Check if username or email already exists
        existing = svc.schema("bitebuilder").table("profiles")\
            .select("id").or_(f"email.eq.{email},username.eq.{username}").execute()

        if existing.data:
            return Response(
                {"error": "User already exists with this email or username"},
                status=400,
            )

        # ✅ Proceed to create auth user
        sb = _sb_public()
        res = sb.auth.sign_up({"email": email, "password": password})
        user = res.user

        # upsert the row in the profiles on supabase
        svc.schema("bitebuilder").table("profiles").upsert({
            "id": user.id,
            "username": username,
            "email": email,
        }).execute()

        # Create Profile locally
        Profile.objects.create(id=user.id, username=username, email=email)

        return Response({"user_id": user.id, "username": username, "email": email})

    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "duplicate key" in msg.lower():
            return Response({"error": "Email is already registered"}, status=400)
        return Response({"error": msg}, status=500)

def send_email(to, subject, body):
    """Send a simple HTML email via SMTP."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"Email sent to {to}")
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        raise

@api_view(["POST"])
def api_login(request):
    data = request.data
    
    try:
        username = validate_string_length(data.get("username", "").strip(), 255, "Username/Email")
        password = data.get("password", "").strip()
        
        if len(password) > 128:
            raise ValidationError("Password is too long")
            
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)
    
    remember = data.get("remember") or False

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=400,
        )

    try:
        # Determine the email from either direct input or username lookup
        if "@" in username:
            email = username
            svc = _sb_service()
            res = (svc.schema("bitebuilder").table("profiles")
                        .select("username")
                        .eq("email", email)
                        .limit(1)
                        .execute()
                    )
            username = res.data[0]["username"]
        else:
            svc = _sb_service()
            # Use profiles schema under the "bitebuilder"
            res = (svc.schema("bitebuilder").table("profiles")
                        .select("email")
                        .eq("username", username)
                        .limit(1)
                        .execute()
                    )
            if not res.data:
                return Response({"error": "User not found."}, status=400)
            email = res.data[0]["email"]

        # Authenticate with Supabase Auth
        sb = _sb_public()
        auth_res = sb.auth.sign_in_with_password({"email": email, "password": password})

        user_id = auth_res.user.id
        admin = (svc.schema("bitebuilder").table("profiles")
                        .select("isadmin")
                        .eq("id", user_id)
                        .limit(1)
                        .execute()
                )
        
        row = (admin.data or [None])[0]
        is_admin = bool(row.get("isadmin"))

        # 🔒 Ensure local Profile exists
        profile, created = Profile.objects.get_or_create(
            id=user_id,
            defaults={"username": username, "email": email},
        )
        if created:
            print(f"[api_login] Created local Profile for {email}")


        # ensure that the is_admin updated
        Profile.objects.update_or_create(
            id=user_id, defaults={"is_admin": is_admin}
        )
                
                
        table = svc.schema("bitebuilder").table("otp_codes")

        def gen_code():
            return f"{random.randint(100000, 999999)}"
        
        # hash the code
        code = gen_code()
        code_hash = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()

        payload = {
            "user_id": auth_res.user.id,
            "email": email,
            "purpose": "login",
            "code": code_hash,
            "expires_at": (timezone.now() + timedelta(minutes=2)).isoformat(),}
        table.upsert(payload, on_conflict="user_id,purpose").execute()

        # ---- send email via your SMTP ----
        body = f"""
        <h2>Login verification code</h2>
        <p>Your one-time code is <b>{code}</b></p>
        <p>This code expires in 2 minutes.</p>
        """
        send_email(email, "Your BiteBuilder login code", body)

        # Store login session in Django
        _start_login_session(request, auth_res.session, auth_res.user, username, email, remember)
        request.session["otp_verified"] = False
        request.session["otp_email"] = email
        request.session["otp_expires_at"] = int(time.time()) + 120  # 2 minute
        request.session.save()

        try:
            profile = Profile.objects.get(id=user_id)
            is_admin = profile.is_admin
        except Profile.DoesNotExist:
            # fallback if profile wasn’t synced yet
            is_admin = False


        return Response(
            {
                "message": "Login successful.",
                "user_id": auth_res.user.id,
                "username": username,
                "email": email,
                "is_admin": is_admin,
            },
            status=200,
        )
    except Exception as e:
        # Surface Supabase errors
        return Response(
            {"error": "Invalid username, email or password."},
            status=400
        )
    
@api_view(["POST"])
def api_verify_otp(request):
    # must have an active login session
    uid = request.session.get("sb_user_id")
    if not uid:
        return Response({"error": "No active session. Please login again."}, status=400)

    if request.session.get("otp_verified") is True:
        return Response({"message": "Already verified"}, status=200)

    try:
        code = validate_string_length(request.data.get("code", "").strip(), 10, "OTP code")
        validate_otp_code(code)
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)

    # session-time window check (fast fail)
    if int(time.time()) > int(request.session.get("otp_expires_at", 0)):
        return Response({"error": "Code expired. Please login again."}, status=400)

    # fetch the OTP for this user+purpose
    svc = _sb_service()
    q = (svc.schema("bitebuilder").table("otp_codes")
           .select("id, code, expires_at")
           .eq("user_id", uid)
           .eq("purpose", "login")
           .limit(1)
           .execute())
    row = q.data[0] if q.data else None
    if not row:
        return Response({"error": "No pending OTP. Please login again."}, status=400)

    # db-side expiry check
    expires_at = row["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if timezone.now() > expires_at:
        return Response({"error": "Code expired. Please request a new one."}, status=400)

    # compare the code
    ok = bcrypt.checkpw(code.encode(), row["code"].encode())
    if not ok:
        return Response({"error": "Incorrect code."}, status=400)
    
    # consume the OTP
    (svc.schema("bitebuilder").table("otp_codes")
        .delete()
        .eq("id", row["id"])
        .execute())

    # success → mark session verified
    request.session["otp_verified"] = True
    request.session.save()
    return Response({"message": "Login successful!"}, status=200)


@api_view(["GET"])
def api_verify_session(request):
    if not request.session.exists(request.session.session_key):
        return Response({"authenticated": False, "reason": "Session expired"})
    user_id = request.session.get("sb_user_id")
    username = request.session.get("sb_username")
    email = request.session.get("sb_email")
    token = request.session.get("sb_access_token")
    verified = request.session.get("otp_verified")
    if not user_id or not token or not verified:
        return Response({"authenticated": False}, status=200)
    
    try:
        profile = Profile.objects.get(id=user_id)
        is_admin = profile.is_admin
    except Profile.DoesNotExist:
        # fallback if profile wasn’t synced yet
        is_admin = False
    return Response({"authenticated": True, "user_id": user_id, "username": username, "email": email, "is_admin": is_admin})


@api_view(["POST"])
def api_logout(request):
    sb = _sb_public()
    sb.auth.sign_out()
    request.session.flush()
    return Response({"message": "Logged out"})



# send code to reset the password
@api_view(["POST"])
def api_resetPassword(request):
    try:
        email = validate_string_length(request.data.get("email", "").strip(), 255, "Email")
        validate_email(email)
        
        password = request.data.get("password", "").strip()
        validate_password_length(password)
        
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)
    
    if not email or not password:
        return Response({"error": "Missing required fields"}, status=400)
    
    try:
        svc = _sb_service()
        res = (svc.schema("bitebuilder").table("profiles")
                    .select("id")
                    .eq("email", email)
                    .limit(1)
                    .execute()
                )
        if not res.data:
            return Response({"error": "Invalid email"}, status=400)
        id = res.data[0]["id"]
        table = svc.schema("bitebuilder").table("otp_codes")

        def gen_code():
            return f"{random.randint(100000, 999999)}"
        
        code = gen_code()
        code_hash = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()

        expires_at = timezone.now() + timedelta(minutes=2)

        payload = {
            "user_id": id,
            "email": email,
            "purpose": "reset",
            "code": code_hash,
            "temp": password,
            "expires_at": expires_at.isoformat(),}
        table.upsert(payload, on_conflict="user_id,purpose").execute()

        # ---- send email via your SMTP ----
        body = f"""
        <h2>Reset password verification code</h2>
        <p>Your one-time code is <b>{code}</b></p>
        <p>This code expires in 2 minutes.</p>
        """
        send_email(email, "Code of your BiteBuilder reset password", body)

        request.session["email"] = email
        request.session["id"] = id
        request.session["expires_at"] = int(time.time()) + 120
        request.session.save()


        return Response(
            {
                "message": "code correct.",
                "user_id": id,
                "email": email,
                "expires_at": int(time.time()) + 120,
            },
            status=200,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return Response({"error": f"Internal error: {str(e)}"}, status=500)


@api_view(["POST"])
# do the reset password
def api_verify_otp_resetPassword(request):
    try:
        code = validate_string_length(request.data.get("code", "").strip(), 10, "OTP code")
        validate_otp_code(code)
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)
        
    id = (request.session.get("id") or "").strip()

    # session-time window check (fast fail)
    if int(time.time()) > int(request.session.get("expires_at", 0)):
        return Response({"error": "Code expired. Please login again."}, status=400)

    # fetch the OTP for this user+purpose
    svc = _sb_service()
    q = (svc.schema("bitebuilder").table("otp_codes")
           .select("id, code, expires_at, temp")
           .eq("user_id", id)
           .eq("purpose", "reset")
           .limit(1)
           .execute())
    row = q.data[0] if q.data else None
    if not row:
        return Response({"error": "No pending OTP. Please try again."}, status=400)

    # db-side expiry check
    expires_at = row["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if timezone.now() > expires_at:
        return Response({"error": "Code expired. Please request a new one."}, status=400)

    # compare the code
    ok = bcrypt.checkpw(code.encode(), row["code"].encode())
    if not ok:
        return Response({"error": "Incorrect code."}, status=400)
    
    svc.auth.admin.update_user_by_id(id, {"password": row["temp"]})

    # consume the OTP
    (svc.schema("bitebuilder").table("otp_codes")
        .delete()
        .eq("id", row["id"])
        .execute())

    request.session.flush()
    # success 
    return Response({"message": "Reset successful!"}, status=200)


@ensure_csrf_cookie
@api_view(["GET"])
def csrf_seed(request):
    return Response({"ok": True})
    