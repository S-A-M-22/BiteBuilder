from collections import defaultdict
from apps.core.models.eaten_meal import EatenMeal
from apps.core.models.goal_nutrient import GoalNutrient


def recalculate_goal_nutrients(user):
    """
    Recalculate total nutrient consumption across all eaten meals for a user.
    Prints all stages for debugging.
    """
    print(f"\n=== Recalculating goal nutrients for user {user.id} ===", flush=True)

    eaten_meals = (
        EatenMeal.objects.filter(user=user)
        .select_related("meal")
        .prefetch_related("meal__items__product__product_nutrients__nutrient")
    )
    print(f"Fetched {eaten_meals.count()} eaten meals", flush=True)

    totals = defaultdict(float)

    for eaten in eaten_meals:
        meal = eaten.meal
        print(f"Processing meal: {meal.name} (id={meal.id})", flush=True)
        for item in meal.items.all():
            qty = item.quantity or 0
            product = item.product
            print(f"  Item: {product.name} (qty={qty})", flush=True)

            nutrients = product.product_nutrients.all()
            if not nutrients.exists():
                print(f"     No nutrients for {product.name}", flush=True)
                continue

            for pn in nutrients:
                try:
                    amount = float(pn.amount_per_100g or 0)
                except (ValueError, TypeError):
                    print(f"     Invalid amount for nutrient {pn.nutrient_id}: {pn.amount_per_100g}", flush=True)
                    amount = 0

                totals[pn.nutrient.id] += amount * qty / 100.0
                print(f"    + {pn.nutrient_id}: {amount * qty / 100.0:.2f}", flush=True)

    print(f"\nAggregated totals (non-zero only):", flush=True)
    for nid, val in totals.items():
        if val:
            print(f"  {nid}: {val:.2f}", flush=True)

    goal_nutrients = GoalNutrient.objects.filter(goal__user=user)
    print(f"\nFound {goal_nutrients.count()} goal nutrients", flush=True)

    for gn in goal_nutrients:
        print(f"[API] nutrient_id type for {gn.id}: {type(gn.nutrient_id)}", flush=True)
        new_val = totals.get(gn.nutrient_id, 0)
        if gn.consumed_amount != new_val:
            print(f"Updating {gn.nutrient_id}: {gn.consumed_amount:.2f} {new_val:.2f}", flush=True)
            gn.consumed_amount = new_val
            gn.save(update_fields=["consumed_amount"])
        else:
            print(f"No change for {gn.nutrient_id} ({gn.consumed_amount:.2f})", flush=True)

    print(f"=== Recalculation complete for user {user.id} ===\n", flush=True)
    return totals
