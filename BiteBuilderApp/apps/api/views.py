from rest_framework import viewsets
from apps.core.models import *
from apps.users.models import Profile
from .serializers import *
from rest_framework.response import Response
from rest_framework import status

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MealWriteSerializer
        return MealSerializer

    def get_queryset(self):
        """Filter meals by Supabase user ID stored in Django session."""
        user_id = self.request.session.get("sb_user_id")
        print(" [MealViewSet] sb_user_id from session:", user_id, flush=True)

        if not user_id:
            # No authenticated session; return empty queryset
            return Meal.objects.none()

        return (
            Meal.objects
            .select_related("user")
            .prefetch_related("items__product__product_nutrients__nutrient")
            .filter(user=user_id)
            .order_by("-date_time")
        )

    def perform_create(self, serializer):
        """Automatically assign the logged-in Supabase user to new meals."""
        user_id = self.request.session.get("sb_user_id")
        if not user_id:
            raise PermissionError("User not authenticated in session.")
        serializer.save(user_id=user_id)


from rest_framework import status
from rest_framework.response import Response

class MealItemViewSet(viewsets.ModelViewSet):
    queryset = MealItem.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MealItemWriteSerializer
        return MealItemSerializer

    def get_queryset(self):
        """Filter meal items by Supabase user ID from Django session."""
        user_id = self.request.session.get("sb_user_id")
        print(" [MealItemViewSet] sb_user_id from session:", user_id, flush=True)

        if not user_id:
            return MealItem.objects.none()

        return (
            MealItem.objects
            .select_related("meal", "product")
            .prefetch_related("product__product_nutrients__nutrient")
            .filter(meal__user=user_id)
            .order_by("-meal__date_time")
        )

    def create(self, request, *args, **kwargs):
        """Use write serializer for input and read serializer for output."""
        write_serializer = MealItemWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        meal_item = write_serializer.save()

        # Re-serialize with the read serializer (hydrated product)
        read_serializer = MealItemSerializer(meal_item, context={"request": request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)



class NutrientViewSet(viewsets.ModelViewSet):
    queryset = Nutrient.objects.all()
    serializer_class = NutrientSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    queryset = Goal.objects.select_related("user")

    def get_queryset(self):
        """Filter goals by Supabase user ID from Django session."""
        user_id = self.request.session.get("sb_user_id")
        print("[GoalViewSet] sb_user_id from session:", user_id, flush=True)

        if not user_id:
            return Goal.objects.none()

        return Goal.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        """Automatically associate new Goal with the Supabase user."""
        user_id = self.request.session.get("sb_user_id")
        if not user_id:
            return Response({"detail": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        # Ensure a corresponding Profile exists — one per Supabase user
        profile, _ = Profile.objects.get_or_create(id=user_id)
        serializer.save(user=profile)

from apps.core.goals.utils import recalculate_goal_nutrients
from django.db import transaction


class GoalNutrientViewSet(viewsets.ModelViewSet):
    """Manage Goal Nutrients and automatically resync totals."""
    queryset = GoalNutrient.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return GoalNutrientWriteSerializer
        return GoalNutrientReadSerializer

    def get_queryset(self):
        user_id = self.request.session.get("sb_user_id")
        print("[GoalNutrientViewSet] sb_user_id from session:", user_id, flush=True)

        if not user_id:
            return GoalNutrient.objects.none()

        qs = GoalNutrient.objects.filter(goal__user_id=user_id)
        goal_id = self.request.query_params.get("goal_id")
        if goal_id:
            qs = qs.filter(goal_id=goal_id)
        return qs

    def perform_create(self, serializer):
        """Attach new GoalNutrient and schedule backend resync post-commit."""
        user_id = self.request.session.get("sb_user_id")
        if not user_id:
            raise PermissionError("User not authenticated in session.")

        goal = Goal.objects.filter(user_id=user_id).first()
        if not goal:
            raise ValueError("Goal not found for user.")

        instance = serializer.save(goal=goal)
        print(f"[GoalNutrientViewSet] Scheduled recalculation after add for user {user_id}", flush=True)
        transaction.on_commit(lambda: recalculate_goal_nutrients(goal.user))
        return instance  # ✅ pass the instance back

    def perform_destroy(self, instance):
        """Recalculate totals after delete (post-commit safe)."""
        user = instance.goal.user
        super().perform_destroy(instance)
        print(f"[GoalNutrientViewSet] Scheduled recalculation after delete for user {user.id}", flush=True)
        transaction.on_commit(lambda: recalculate_goal_nutrients(user))

    def create(self, request, *args, **kwargs):
        """Create + return hydrated response with recalculation deferred correctly."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)  # ✅ don’t call save() again
        read_serializer = GoalNutrientReadSerializer(instance, context={"request": request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

class EatenMealViewSet(viewsets.ModelViewSet):
    queryset = EatenMeal.objects.select_related("meal", "meal__user")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EatenMealWriteSerializer
        return EatenMealReadSerializer

    def get_queryset(self):
        """Filter eaten meals by Supabase user ID stored in session."""
        user_id = self.request.session.get("sb_user_id")
        print("[EatenMealViewSet] sb_user_id from session:", user_id, flush=True)

        if not user_id:
            return EatenMeal.objects.none()

        return (
            EatenMeal.objects
            .select_related("meal", "meal__user")
            .prefetch_related("meal__items__product__product_nutrients__nutrient")
            # ✅ Correct traversal through meal → user
            .filter(meal__user=user_id)
            .order_by("-eaten_at")
        )

    def create(self, request, *args, **kwargs):
        user_id = self.request.session.get("sb_user_id")
        if not user_id:
            return Response({"detail": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meal = serializer.validated_data.get("meal")

        if str(meal.user_id) != str(user_id):
            return Response({"detail": "Cannot log meals for another user."}, status=status.HTTP_403_FORBIDDEN)

        instance = serializer.save()

        # trigger goal nutrient recomputation
        recalculate_goal_nutrients(instance.user)

        read_serializer = EatenMealReadSerializer(instance, context={"request": request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
