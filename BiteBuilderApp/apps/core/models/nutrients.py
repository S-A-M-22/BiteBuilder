import uuid
from django.db import models

class Nutrient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Canonical internal code, e.g. 'energy_kj', 'protein', 'sugars'"
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Display name, e.g. 'Energy (kJ)', 'Protein'"
    )

    UNIT_CHOICES = [
        ("g", "g"),
        ("mg", "mg"),
        ("µg", "µg"),
        ("kJ", "kJ"),
        ("kcal", "kcal"),
        ("%", "%"),
        ("per_serving", "per_serving"),
    ]
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)

    category = models.CharField(
        max_length=50,
        choices=[
            ("macronutrient", "Macronutrient"),
            ("vitamin", "Vitamin"),
            ("mineral", "Mineral"),
        ],
        null=True,
        blank=True,
    )

    display_order = models.PositiveSmallIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = "bitebuilder.nutrients"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["code"]),
        ]
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        self.code = self.code.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.unit})"
