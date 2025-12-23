# ===============================================
# apps/core/services/fatsecret_enrichment.py
# ===============================================
"""
FatSecret enrichment helper — fill missing nutrients for products.
Depends on fatsecret_oauth2_client and woolies_api canonical schema.
"""


import datetime
from apps.services.fatsecret_oauth1_client import analyze_meal_text
from apps.services.woolies_api import DEFAULT_NUTRIENT_UNITS


FATSECRET_CANON_MAP = {
    "calories": "energy-kcal",
    "carbohydrate": "carbohydrates",
    "protein": "proteins",
    "fat": "fat",
    "saturated_fat": "fat-saturated",
    "polyunsaturated_fat": "polyunsaturated-fat",
    "monounsaturated_fat": "monounsaturated-fat",
    "cholesterol": "cholesterol",
    "sodium": "sodium",
    "potassium": "potassium",
    "fiber": "fiber",
    "sugar": "carbohydrates-sugars",
    "vitamin_a": "vitamin-a",
    "vitamin_c": "vitamin-c",
    "calcium": "calcium",
    "iron": "iron",
}


from datetime import datetime
import json

def extract_nutrients_from_fatsecret(meal_text: str) -> dict:
    """
    Run FatSecret NLP on meal_text and return merged per-100 dict of nutrients,
    printing debug information for inspection.
    """
    print(f"\n[FatSecret NLP]  Starting extraction for: '{meal_text}'")

    data = analyze_meal_text(meal_text, include_food_data=True)
    if not data:
        print("[FatSecret NLP]  No data returned from API.")
        return {"nutrients": {}, "provenance": []}

    if "food_response" not in data:
        print("[FatSecret NLP]  No 'food_response' key in response.")
        print("[FatSecret NLP] Raw data:", json.dumps(data, indent=2)[:1000], "...")
        return {"nutrients": {}, "provenance": []}

    print(f"[FatSecret NLP] Found {len(data['food_response'])} food_response entries")

    nutrients: dict[str, dict] = {}
    provenance: list[dict] = []

    for entry in data.get("food_response", []):
        eaten = entry.get("eaten", {}) or {}
        food = entry.get("food", {}) or {}
        content = eaten.get("total_nutritional_content", {}) or {}

        provenance.append({
            "food_id": entry.get("food_id") or food.get("food_id"),
            "food_entry_name": entry.get("food_entry_name"),
            "food_name": food.get("food_name"),
            "food_type": food.get("food_type"),
            "food_url": food.get("food_url"),
        })

        for k, v in content.items():
            canon_key = FATSECRET_CANON_MAP.get(k)
            if not canon_key:
                continue
            try:
                val = float(v)
            except (TypeError, ValueError):
                continue

            unit = DEFAULT_NUTRIENT_UNITS.get(canon_key, "g")
            nutrients.setdefault(
                canon_key, {"label": canon_key, "per_100": None, "per_serving": None}
            )
            nutrients[canon_key]["per_100"] = {"value": val, "unit": unit}

    print(f"[FatSecret NLP]  Extracted {len(nutrients)} nutrients total")
    print(f"[FatSecret NLP] Provenance: {json.dumps(provenance, indent=2)}\n")

    return {"nutrients": nutrients, "provenance": provenance}


def enrich_product_with_fatsecret(product: dict) -> dict:
    """
    Patch missing or empty product['nutrition'] using FatSecret NLP data,
    with provenance of the matched FatSecret food(s).
    """
    name = product.get("name") or product.get("description")
    print(f"\n[FatSecret Enrichment]  Enriching product: {name!r}")

    if not name:
        print("[FatSecret Enrichment]  No name or description; skipping.")
        return product

    result = extract_nutrients_from_fatsecret(name)
    fs_nutrients = result.get("nutrients", {})
    provenance = result.get("provenance", [])

    if not fs_nutrients:
        print(f"[FatSecret Enrichment]  No nutrients found for '{name}'")
        return product

    nutrition = product.get("nutrition", {}) or {}
    added_keys = []

    for key, node in fs_nutrients.items():
        if key not in nutrition or not nutrition[key].get("per_100"):
            nutrition[key] = node
            added_keys.append(key)

    product["nutrition"] = nutrition

    product.setdefault("enrichment", {})
    product["enrichment"]["fatsecret"] = {
        "source_foods": provenance,
        "method": "fatsecret_nlp",
        "timestamp": datetime.utcnow().isoformat(),
    }

    print(f"[FatSecret Enrichment]  Added/updated keys: {added_keys}")
    print(f"[FatSecret Enrichment] Provenance count: {len(provenance)}\n")

    return product
