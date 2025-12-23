# apps/api/serializers/product_serializers.py
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import Product, ProductNutrient, Nutrient


# --- Nutrient (base) ---
class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = ["id", "code", "name", "unit", "category"]


# --- ProductNutrient (read) ---
class ProductNutrientReadSerializer(serializers.ModelSerializer):
    nutrient = NutrientSerializer(read_only=True)

    class Meta:
        model = ProductNutrient
        fields = ["nutrient", "amount_per_100g", "amount_per_serving"]


# --- ProductNutrient (write) ---
class ProductNutrientWriteSerializer(serializers.ModelSerializer):
    nutrient = serializers.PrimaryKeyRelatedField(queryset=Nutrient.objects.all())
    amount_per_100g = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100000)]
    )
    amount_per_serving = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100000)]
    )
    

    class Meta:
        model = ProductNutrient
        fields = ["nutrient", "amount_per_100g", "amount_per_serving"]




# --- Product (read) ---
class ProductReadSerializer(serializers.ModelSerializer):
    product_nutrients = ProductNutrientReadSerializer(many=True, read_only=True)
    enrichment_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_enrichment_status(self, obj):
        if getattr(obj, "last_enriched_at", None):
            return "ready"
        if getattr(obj, "needs_enrichment", None):
            return "queued"
        return "none"


# --- Product (write) ---
# --- Product (write) ---
class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Used for user-created or enrichment saves.
    Excludes nested relations.
    """
    name = serializers.CharField(max_length=255)
    brand = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,  # ← ADD THIS
    )
    description = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        allow_null=True,  # ← ADD THIS
    )
    size = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,  # ← ADD THIS
    )
    barcode = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
        allow_null=True,  # ← ADD THIS
    )
    allergens = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True,  # ← ADD THIS
    )
    
    price_current = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    
    serving_size_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100000)]
    )
    
    servings_per_pack = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10000)]
    )

    price_was = serializers.DecimalField(
    max_digits=10,
    decimal_places=2,
    required=False,
    allow_null=True,
    validators=[MinValueValidator(0), MaxValueValidator(999999)],
    )

    cup_price_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=4,
        required=False,
        allow_null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999999)],
    )

    cup_price_unit = serializers.CharField(
        max_length=16,
        required=False,
        allow_blank=True,
        allow_null=True,
    )


    class Meta:
        model = Product
        fields = [
        "barcode",
        "name",
        "brand",
        "description",
        "size",
        "price_current",
        "price_was",          # ← add this
        "is_on_special",
        "cup_price_value",    # ← add this
        "cup_price_unit",     # ← add this
        "image_url",
        "product_url",
        "health_star",
        "allergens",
        "serving_size_value",
        "serving_size_unit",
        "servings_per_pack",
        "nutrition_basis",
        "primary_source",
    ]
        extra_kwargs = {
            # 🔹 disable DRF's default unique check so `update_or_create()` can handle it
            "barcode": {"validators": []},
        }
    
    def validate_name(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Product name is required")
        if len(value) > 255:
            raise serializers.ValidationError("Product name exceeds maximum length of 255")
        return value.strip()
    
    def validate_description(self, value):
        if value and len(value) > 2000:
            raise serializers.ValidationError("Description exceeds maximum length of 2000")
        return value
    
    def validate_allergens(self, value):
        if value and len(value) > 1000:
            raise serializers.ValidationError("Allergens text exceeds maximum length of 1000")
        return value
