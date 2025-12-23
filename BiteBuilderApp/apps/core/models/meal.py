from django.db import models
from ...users.models import Profile
from django.utils import timezone
import uuid
from .product import Product

class Meal(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH     = "lunch",     "Lunch"
        DINNER    = "dinner",    "Dinner"
        SNACK     = "snack",     "Snack"

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(Profile, on_delete=models.CASCADE, db_column="user_id",
                                    related_name="meals")
    meal_type   = models.CharField(max_length=10, choices=MealType.choices)
    date_time   = models.DateTimeField(default=timezone.now)
    notes       = models.TextField(null=True, blank=True)
    name        = models.CharField(          # 👈 new field
        max_length=100,
        null=True,
        blank=True,
        help_text="Optional custom name, e.g. 'Post-workout lunch' or 'Sunday dinner'")


    class Meta:
        db_table = "bitebuilder.meals"   # ← use your actual table name
        indexes = [
            models.Index(fields=["user", "date_time"]),
            models.Index(fields=["user", "meal_type", "date_time"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.meal_type} @ {self.date_time:%Y-%m-%d %H:%M}"
    
    def recalc_total(self):
        total = sum(item.calories or 0 for item in self.items.all())
        self.total_calories = total
        self.save(update_fields=["total_calories"])

class MealItem(models.Model):
    """
    Through table for Meal ↔ Product with per-item quantity and calories.
    """
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal     = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="items",
                                 db_column="meal_id")
    # Product barcode FK
    product = models.ForeignKey(
        "Product",
        to_field="barcode",
        on_delete=models.CASCADE,
        related_name="meal_items",
        db_column="product_barcode",
    )
    quantity = models.FloatField(help_text="Amount eaten in product's unit (e.g., grams)")

    class Meta:
        db_table = "bitebuilder.meal_item"
        indexes = [models.Index(fields=["meal"]), models.Index(fields=["product"])]
        # If you want one row per product per meal, uncomment:
        # unique_together = ("meal", "product")

    def __str__(self):
        return f"{self.meal_id} · {self.product_id} · {self.quantity}"