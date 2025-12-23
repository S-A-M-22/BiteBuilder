from django.http import JsonResponse

class EnforceOtpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ✅ Skip non-API paths completely (frontend, favicon, admin, etc.)
        if not path.startswith("/api/"):
            return self.get_response(request)

        # ✅ Explicit allowlist for unauthenticated API routes
        allowlist = (
            "/api/auth/login/",
            "/api/auth/register/",
            "/api/auth/verify_otp/",
            "/api/auth/verify/",
            "/api/auth/logout/",
            "/api/auth/resetPassword/",
            "/api/auth/api_otp_resetPassword/",
        )

        if any(path.startswith(p) for p in allowlist):
            return self.get_response(request)

        # ⚔️ Enforce OTP only for authenticated API routes
        if request.session.get("sb_user_id") and not request.session.get("otp_verified", False):
            return JsonResponse({"error": "OTP required"}, status=423)
        
        elif not request.session.get("sb_user_id"):
            return JsonResponse({"error": "invalid session"}, status=423)

        return self.get_response(request)
