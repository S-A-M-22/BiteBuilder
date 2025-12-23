from django.core.management.base import BaseCommand
from apps.core.models.nutrients import Nutrient


SEED_NUTRIENTS = [
    # Macronutrients
    ("energy_kj", "Energy (kJ)", "kJ", "macronutrient"),
    ("energy_kcal", "Energy (kcal)", "kcal", "macronutrient"),
    ("protein", "Protein", "g", "macronutrient"),
    ("fat_total", "Total Fat", "g", "macronutrient"),
    ("fat_saturated", "Saturated Fat", "g", "macronutrient"),
    ("carbohydrate", "Carbohydrates", "g", "macronutrient"),
    ("sugars", "Sugars", "g", "macronutrient"),
    ("fiber", "Dietary Fiber", "g", "macronutrient"),

    # Minerals
    ("sodium", "Sodium", "mg", "mineral"),
    ("calcium", "Calcium", "mg", "mineral"),
    ("iron", "Iron", "mg", "mineral"),
    ("magnesium", "Magnesium", "mg", "mineral"),
    ("potassium", "Potassium", "mg", "mineral"),
    ("phosphorus", "Phosphorus", "mg", "mineral"),
    ("zinc", "Zinc", "mg", "mineral"),

    # Vitamins
    ("vitamin_a", "Vitamin A", "µg", "vitamin"),
    ("vitamin_c", "Vitamin C", "mg", "vitamin"),
    ("vitamin_d", "Vitamin D", "µg", "vitamin"),
    ("vitamin_b6", "Vitamin B6", "mg", "vitamin"),
    ("vitamin_b12", "Vitamin B12", "µg", "vitamin"),
    ("vitamin_e", "Vitamin E", "mg", "vitamin"),
    ("vitamin_k", "Vitamin K", "µg", "vitamin"),
    ("folate", "Folate", "µg", "vitamin"),
]

class Command(BaseCommand):
    help = "Seeds the database with canonical nutrient definitions"

    def handle(self, *args, **options):
        created, updated = 0, 0

        for code, name, unit, category in SEED_NUTRIENTS:
            obj, is_created = Nutrient.objects.update_or_create(
                code=code,
                defaults={"name": name, "unit": unit, "category": category},
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Nutrient seeding complete: {created} created, {updated} updated")
        )
