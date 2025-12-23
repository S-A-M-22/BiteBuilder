# apps/api/api_profile.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import os

from ..users.views import (
    _sb_service,
)



@csrf_exempt
@api_view(["GET"])
def fetchProfile(request):
    id = request.session.get("sb_user_id")
    if not id:
        return Response({"error": "No active session. Please login again."}, status=400)
    
    try: 
        svc = _sb_service()
        q = (svc.schema("bitebuilder").table("profiles")
            .select("username, email, age, gender, height_cm, weight_kg, postcode")
            .eq("id", id)
            .limit(1)
            .execute())
        
        row = q.data[0] if q.data else None
        if not row:
            return Response({"error": "No profile found."}, status=400)
        
        return Response(
            {
                "message": "fectch correctly.",
                "id": id,
                "username": row["username"],
                "email": row["email"],
                "age": row["age"],
                "gender": row["gender"],
                "height_cm": row["height_cm"],
                "weight_kg": row["weight_kg"],
                "postcode": row["postcode"],
            },
            status=200,
        )
        
    except:
        return Response({"error: not such user."}, status=400)
    

@csrf_exempt
@api_view(["POST"])
def updateProfile(request):
    # check the session is live
    uid = request.session.get("sb_user_id")
    if not uid:
        return Response({"error": "No active session."}, status=401)

    try:
        patch = request.data or {}
        if not patch:
            return Response({"error": "No allowed fields to update."}, status=400)

        svc = _sb_service()

        # update the profile
        (
            svc.schema("bitebuilder")
               .table("profiles")
               .update(patch)
               .eq("id", uid)
               .execute()
        )

        # Fetch updated profile
        res = (
            svc.schema("bitebuilder")
               .table("profiles")
               .select("id, username, email, age, gender, height_cm, weight_kg, postcode")
               .eq("id", uid)
               .single()
               .execute()
        )

        row = res.data
        if not row:
            return Response({"error": "Profile not found."}, status=404)

        return Response(row, status=200)

    except Exception as e:
        # bubble up useful info while developing
        return Response({"error": f"{e}"}, status=400)
    

    
