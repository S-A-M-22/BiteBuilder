# apps/core/models/product.py
import uuid
from django.db import models

from apps.users.models import Profile

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barcode = models.CharField(max_length=32, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)

    price_current = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_was = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_on_special = models.BooleanField(default=False)

    cup_price_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    cup_price_unit = models.CharField(max_length=16, null=True, blank=True)
    
    image_url = models.URLField(null=True, blank=True)
    product_url = models.URLField(null=True, blank=True)
    health_star = models.CharField(max_length=10, null=True, blank=True)
    allergens = models.TextField(null=True, blank=True)

    serving_size_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    serving_size_unit = models.CharField(max_length=8, null=True, blank=True)
    servings_per_pack = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    nutrition_basis = models.CharField(
        max_length=16,
        choices=[("per_100g", "per_100g"), ("per_serving", "per_serving")],
        null=True, blank=True
    )

    primary_source = models.CharField(
        max_length=32,
        choices=[("woolworths", "Woolworths"), ("openfoodfacts", "OpenFoodFacts"), ("user_added", "User Added")],
        default="woolworths"
    )

    last_enriched_at = models.DateTimeField(null=True, blank=True)
    enrichment_attempts = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.primary_source})"


    class Meta:
        indexes = [
            models.Index(fields=["barcode"]),
            models.Index(fields=["name"]),
            models.Index(fields=["brand"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.barcode or 'no-barcode'})"
