from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
import re

from apps.core.models.eaten_meal import EatenMeal
from apps.core.models.product import Product
from apps.api.product_serializers import ProductReadSerializer
from apps.core.models import  Meal, Goal, Nutrient, GoalNutrient, MealItem
from apps.users.models import Profile



class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "username", "email", "is_admin"]
        read_only_fields = ["id"]
    
    def validate_username(self, value):
        if len(value) > 32:
            raise serializers.ValidationError("Username exceeds maximum length of 32")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")
        return value

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = "__all__"

# For POST/PUT/PATCH (IDs only)
class GoalNutrientWriteSerializer(serializers.ModelSerializer):
    goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all())
    nutrient = serializers.PrimaryKeyRelatedField(queryset=Nutrient.objects.all())
    target_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1000000)]
    )
    
    class Meta:
        model = GoalNutrient
        fields = "__all__"
    
    def validate_target_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Target amount cannot be negative")
        if value > 1000000:
            raise serializers.ValidationError("Target amount is too large")
        return value

# For GET (nested nutrient info)
class GoalNutrientReadSerializer(serializers.ModelSerializer):
    goal = serializers.PrimaryKeyRelatedField(read_only=True)
    nutrient = NutrientSerializer(read_only=True)  # full object
    class Meta:
        model = GoalNutrient
        fields = "__all__"

class MealItemSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)

    class Meta:
        model = MealItem
        fields = [
            "id",
            "quantity",
            "meal",
            "product",
        ]
class MealItemWriteSerializer(serializers.ModelSerializer):
    meal = serializers.PrimaryKeyRelatedField(
        queryset=Meal.objects.all()
    )
    product = serializers.SlugRelatedField(
        slug_field="barcode",
        queryset=Product.objects.all()
    )
    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100000)]
    )

    class Meta:
        model = MealItem
        fields = ["meal", "product", "quantity"]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        if value > 100000:
            raise serializers.ValidationError("Quantity is too large")
        return value



class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)

    class Meta:
        model = Meal
        fields = [
            "id",
            "user",
            "meal_type",
            "name",       #  new field
            "date_time",
            "notes",
            "items",
        ]


class MealWriteSerializer(serializers.ModelSerializer):
    items = MealItemWriteSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    class Meta:
        model = Meal
        fields = [
            "id",
            "user",
            "meal_type",
            "name",       #  new field
            "date_time",
            "notes",
            "items",
        ]
    
    def validate_name(self, value):
        if value and len(value) > 255:
            raise serializers.ValidationError("Name exceeds maximum length of 255")
        return value.strip() if value else value
    
    def validate_notes(self, value):
        if value and len(value) > 1000:
            raise serializers.ValidationError("Notes exceed maximum length of 1000")
        return value.strip() if value else value

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        meal = Meal.objects.create(**validated_data)
        for item_data in items_data:
            MealItem.objects.create(meal=meal, **item_data)
        return meal



# ----------------------------
# WRITE SERIALIZER
# ----------------------------
class EatenMealWriteSerializer(serializers.ModelSerializer):
    """
    Used for POST (user eats a meal).
    Accepts user ID + meal ID only.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    meal = serializers.PrimaryKeyRelatedField(queryset=Meal.objects.all())

    class Meta:
        model = EatenMeal
        fields = ["id", "user", "meal", "eaten_at"]
        read_only_fields = ["id", "eaten_at"]


# ----------------------------
# READ SERIALIZER
# ----------------------------
class EatenMealReadSerializer(serializers.ModelSerializer):
    """
    Used for GET (show eaten meal history).
    Returns nested Meal info.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    meal = MealSerializer(read_only=True)

    class Meta:
        model = EatenMeal
        fields = ["id", "user", "meal", "eaten_at"]