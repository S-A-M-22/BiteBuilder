
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..users.models import Profile

from ..users.views import (
    _sb_service,
)

PAGE_SIZE_DEFAULT = 10

def _serialize_profile(p: Profile) -> dict:
    # Keep only the fields your frontend needs
    return {
        "id": p.id,
        "username": p.username,
        "email": p.email,
        "is_admin": getattr(p, "is_admin", False),
    }

_SB_TO_LOCAL = {
    "id":   "id",
    "username":  "username",
    "email":     "email",
    "isadmin":   "is_admin",
}


def _safe_is_empty(val):
    return val is None or (isinstance(val, str) and val.strip() == "")

def _upsert_local_from_row(row, Profile):
    """Create local row if missing; otherwise fill only empty local fields."""
    uid = row.row.get("id")
    if not uid:
        return

    obj, created = Profile.objects.get_or_create(
        **{_serialize_profile["id"]: uid},
        defaults={_serialize_profile[k]: row.get(k) for k in _serialize_profile if k != "user_id"}
    )
    if created:
        return

    changed = False
    for sb_key, local_key in _serialize_profile.items():
        if sb_key == "id":
            continue
        src = row.get(sb_key)
        if not _safe_is_empty(src) and _safe_is_empty(getattr(obj, local_key, None)):
            setattr(obj, local_key, src)
            changed = True
    if changed:
        obj.save()

def _sync_all_profiles_from_supabase(sb, Profile, *, delete_locals_not_in_supabase=False):
    """
    Pull ALL rows from Supabase bitebuilder.profiles and upsert into local Profile.
    Overwrites local values with Supabase values. Creates missing rows.
    Optionally deletes local rows whose auth_uid no longer exists in Supabase.
    """
    batch = 1000
    start = 0
    seen_uids = set()

    while True:
        res = (
            sb.schema("bitebuilder").table("profiles")
              .select("id,username,email,isadmin")
              .range(start, start + batch - 1)
              .execute()
        )
        rows = res.data or []
        if not rows:
            break

        for r in rows:
            uid = r.get("id")
            if not uid:
                continue
            seen_uids.add(uid)

            # Build defaults dict by mapping fields
            defaults = { _SB_TO_LOCAL[k]: r.get(k) for k in _SB_TO_LOCAL if k != "id" }

            # Upsert: overwrite everything from Supabase
            Profile.objects.update_or_create(
                **{ _SB_TO_LOCAL["id"]: uid },
                defaults=defaults
            )

        if len(rows) < batch:
            break
        start += batch

    if delete_locals_not_in_supabase and seen_uids:
        Profile.objects.exclude(id__in=seen_uids).delete()

def _build_page_link(request, page_number):
    if page_number is None:
        return None
    q = request.GET.copy()
    q["page"] = str(page_number)
    # return a relative URL; your TS expects string | null
    return f"{request.path}?{q.urlencode()}"

@api_view(["GET"])
def list_users(request):
    """
    GET /users/?search=&page=1[&page_size=10]
    """
    search = (request.GET.get("search") or "").strip()
    
    # Validate search input length
    if len(search) > 255:
        return Response({"error": "Search query exceeds maximum length of 255"}, status=400)
    
    page_num = request.GET.get("page") or "1"
    
    # Validate and sanitize page_size
    try:
        page_size = int(request.GET.get("page_size") or PAGE_SIZE_DEFAULT)
        if page_size < 1 or page_size > 100:
            page_size = PAGE_SIZE_DEFAULT
    except ValueError:
        page_size = PAGE_SIZE_DEFAULT

    
    
    #  sync from Supabase
    try:
        sb = _sb_service()
        _sync_all_profiles_from_supabase(sb, Profile, delete_locals_not_in_supabase=True)
    except Exception as e:
        # Don’t fail the list if sync has an issue
        print(" sync from Supabase failed:", e)

    qs = Profile.objects.all().order_by("-id")
    if search:
        # name/email filter — tweak fields as needed
        qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search))

    paginator = Paginator(qs, page_size)
    try:
        page = paginator.page(int(page_num))
    except (ValueError, EmptyPage):
        page = paginator.page(1)

    data = [_serialize_profile(p) for p in page.object_list]

    resp = {
        "results": data,
        "count": paginator.count,
        "next": _build_page_link(request, page.next_page_number() if page.has_next() else None),
        "previous": _build_page_link(request, page.previous_page_number() if page.has_previous() else None),
    }
    return Response(resp, status=200)

@csrf_exempt
@api_view(["POST"])
def delete_user(request, user_id: str):
    """
    DELETE 
    """
    current = request.session.get("sb_user_id")
    if (current == user_id):
        return Response({"error": "You can not delete yourselves"}, status=404)
    
    try:
        obj = Profile.objects.get(pk=user_id)
    except Profile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    obj.delete()

    # --- delete from Supabase Authentication ---
    try:
        sb = _sb_service() 
        sb.auth.admin.delete_user(user_id) 
    except Exception as e:
        return Response({"error": f"Supabase Auth delete failed: {e}"}, status=502)

    return Response({"message": "Deleted!"}, status=200)

@csrf_exempt
@api_view(["POST"])
def isAdmin(request):
    try:
        sb = _sb_service()

        uid = request.session.get("sb_user_id")
        if not uid:
            return Response({"error": "No user session found"}, status=401)

        res = (
            sb.schema("bitebuilder")
              .table("profiles")
              .select("isadmin")
              .eq("id", uid)
              .limit(1)
              .execute()
        )

        if res.data and len(res.data) > 0:
            is_admin = bool(res.data[0].get("isadmin", False))
            return Response({"is_admin": is_admin}, status=200)

        return Response({"error": "User not found"}, status=404)

    except Exception as e:
        return Response({"error": "isAdmin check failed"}, status=500)