from supabase import create_client
import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # server-only!

def _sb_public():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def _sb_service():
    return create_client(SUPABASE_URL, SERVICE_KEY)


def _sb_with_token(access_token: str):
    """Return a client that sends the user's JWT to PostgREST (RLS on)."""
    c = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    c.postgrest.auth(access_token)
    return c


def _start_login_session(request, session, user, username, email, remember: bool):
    request.session["sb_access_token"] = session.access_token
    request.session["sb_user_id"] = user.id
    request.session["sb_username"] = username
    request.session["sb_email"] = email
    # 1 days
    request.session.set_expiry(60 * 60 * 24 if remember else 0)


