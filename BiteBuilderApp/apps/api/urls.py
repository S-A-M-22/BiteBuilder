from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.services.api_store_views import api_stores_nearby

from ..core.views.products import ProductViewSet


# ----------------------------------------------
# ViewSets
# ----------------------------------------------
from .views import (
    EatenMealViewSet,
    MealItemViewSet,
    MealViewSet,
    GoalViewSet,
    NutrientViewSet,
    ProfileViewSet,
    GoalNutrientViewSet,
)

# ----------------------------------------------
# Auth Views
# ----------------------------------------------
from . import api_user_views, api_profile, api_admin


# =========================================================
# CUSTOM API ROOT
# =========================================================
@api_view(["GET"])
def custom_api_root(request, format=None):
    """
    Root endpoint listing all top-level API resources and auth routes.
    """
    base = request.build_absolute_uri  # short alias
    return Response({
        "models": {
            "products": base("products/"),
            "meals": base("meals/"),
            "meal_items": base("meal-items/"),
            "goals": base("goals/"),
            "goal_nutrients": base("goal-nutrients/"),
            "nutrients": base("nutrients/"),
            "profile": base("profile/"),
            
        },
        "auth": {
            "register": base("auth/register/"),
            "login": base("auth/login/"),
            "api_verify_otp": base("auth/verify_otp/"),
            "verify": base("auth/verify/"),
            "resetPassword": base("auth/resetPassword/"),
            "api_otp_resetPassword": base("auth/api_otp_resetPassword/"),
            "logout": base("auth/logout/"),
            "fetchProfile": base("fetch_profile/"),
            "updateProfile": base("update_Profile/"),
            "csrf": base("csrf/seed/"),
        },

        "adminUser":{
            "listUsers": base("adminUser/listUsers"),
            "deleteUser": base("adminUser/deleteUser/<str:uid>"),
            "isAdmin": base("adminUser/isAdmin"),
        }
    })


# =========================================================
# DRF ROUTER — for all ModelViewSets
# =========================================================
router = DefaultRouter()
router.register("meals", MealViewSet)
router.register("meal-items", MealItemViewSet)
router.register("goals", GoalViewSet)
router.register("goal-nutrients", GoalNutrientViewSet)
router.register("nutrients", NutrientViewSet)
router.register("profile", ProfileViewSet)
router.register(r"products", ProductViewSet, basename="product")
router.register("eaten-meals", EatenMealViewSet)




# =========================================================
# AUTH ROUTES — function-based views
# =========================================================
auth_patterns = [
    path("register/", api_user_views.api_register, name="api_register"),
    path("login/", api_user_views.api_login, name="api_login"),
    path("verify_otp/", api_user_views.api_verify_otp, name="api_verify_otp"),
    path("verify/", api_user_views.api_verify_session, name="api_verify_session"),
    path("logout/", api_user_views.api_logout, name="api_logout"),
    path("resetPassword/", api_user_views.api_resetPassword, name="resetPassword"),
    path("api_otp_resetPassword/", api_user_views.api_verify_otp_resetPassword, name="api_otp_resetPassword"),

    path("fetch_profile/", api_profile.fetchProfile, name="fetchProfile"),
    path("update_profile/", api_profile.updateProfile, name="updateProfile"),
    
    path("csrf/seed/", api_user_views.csrf_seed, name="csrf"),

]

# =========================================================
# ADMIN ROUTES
# =========================================================
admin_patterns = [
    path("listUsers/", api_admin.list_users, name="listUsers"),
    path("deleteUser/<str:user_id>/", api_admin.delete_user, name="deleteUser"),
    path("isAdmin/", api_admin.isAdmin, name="isAdmin"),
]


# =========================================================
# COMBINED URL PATTERNS
# =========================================================
urlpatterns = [
    path("", custom_api_root),                 # → /api/
    path("auth/", include((auth_patterns, "auth"))),  # → /api/auth/...
    path("adminUser/", include((admin_patterns, "adminUser"))),  # → /api/adminUser/...
    path("stores/nearby/", api_stores_nearby),
    *router.urls,                              # → /api/products/, /api/goals/, etc.
]
