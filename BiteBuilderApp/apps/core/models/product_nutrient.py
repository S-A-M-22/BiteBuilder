# apps/core/models/product_nutrient.py
import uuid
from django.db import models
from .product import Product
from .nutrients import Nutrient

class ProductNutrient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_nutrients",
    )
    nutrient = models.ForeignKey(
        Nutrient,
        on_delete=models.CASCADE,
        related_name="nutrient_products",
    )

    amount_per_100g = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        help_text="Amount per 100g or 100mL, depending on product basis."
    )
    amount_per_serving = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )

    class Meta:
        db_table = "bitebuilder.product_nutrient"
        unique_together = ("product", "nutrient")
        indexes = [
            models.Index(fields=["product", "nutrient"]),
            models.Index(fields=["nutrient"]),
        ]

    def __str__(self):
        return f"{self.product.name} → {self.nutrient.name}: {self.amount_per_100g} per 100g"
