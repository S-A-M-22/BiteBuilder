# apps/core/services/woolies_api.py
# --------------------------------
# Woolworths search scraper with full normalization for BiteBuilder/FoodPartsPicker
# - Uses Woolies public JSON search endpoint (no RapidAPI, no HTML scraping)
# - Returns a universal, source-agnostic normalized dict per product
# - Optional Django cache + ingestion helpers included

from __future__ import annotations
import json
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
import requests

# --- Optional Django cache (safe if not in Django context) ---
try:
    import django
    from django.conf import settings
    from django.core.cache import cache  # type: ignore

    _HAS_DJANGO_CACHE = settings.configured
except Exception:
    cache = None  # type: ignore
    _HAS_DJANGO_CACHE = False


# ============================================================
# Config
# ============================================================
WOLLIES_SEARCH_URL = "https://www.woolworths.com.au/apis/ui/Search/products"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
CACHE_TTL_S = 60 * 60 * 12  # 12 hours
DEFAULT_CURRENCY = "AUD"


# ============================================================
# String + unit normalization utilities
# ============================================================
HTML_TAG_RE = re.compile(r"<.*?>", re.DOTALL)


def strip_html(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    return HTML_TAG_RE.sub("", s).strip()


def clean_numeric_unit(value: str) -> Dict[str, Optional[Any]]:
    """
    Parse '44.0mg' -> {'value': 44.0, 'unit': 'mg'}
    Parse '<1g'    -> {'value': 1.0, 'unit': 'g'} (we coerce <1 to 1.0)
    """
    if not value:
        return {"value": None, "unit": None}
    v = value.strip()
    # handle "<1g"
    if v.startswith("<"):
        v = v[1:]
    m = re.match(r"^\s*([\d.]+)\s*([a-zA-Zμ]+)\s*$", v)
    if not m:
        # Sometimes the API provides bare numbers (e.g., "12.0") -> no unit
        m2 = re.match(r"^\s*([\d.]+)\s*$", v)
        if m2:
            try:
                return {"value": float(m2.group(1)), "unit": None}
            except ValueError:
                return {"value": None, "unit": None}
        return {"value": None, "unit": None}
    try:
        num = float(m.group(1))
    except ValueError:
        num = None
    unit = _canon_unit(m.group(2))
    return {"value": num, "unit": unit}


def parse_serving_size(value: Optional[str]) -> Dict[str, Optional[Any]]:
    """
    Example: '250.0 ML' -> {'value': 250.0, 'unit': 'ml'}
             '30 g'     -> {'value': 30.0, 'unit': 'g'}
    """
    if not value:
        return {"value": None, "unit": None}
    v = value.strip()
    m = re.match(r"^\s*([\d.]+)\s*([a-zA-Zμ]+)\s*$", v, flags=re.IGNORECASE)
    if not m:
        return {"value": None, "unit": None}
    try:
        num = float(m.group(1))
    except ValueError:
        num = None
    unit = m.group(2).lower()
    return {"value": num, "unit": unit}


# ============================================================
# Nutrition normalization
# ============================================================
# Human → canonical label
HUMAN_LABEL_MAP = {
    "fat, total": "Fat (Total)",
    "fat total": "Fat (Total)",
    "saturated": "Fat (Saturated)",
    "carbohydrate, total": "Carbohydrate (Total)",
    "carbohydrate total": "Carbohydrate (Total)",
    "sugars": "Carbohydrate (Sugars)",
    "dietary fibre": "Fibre",
    "fiber": "Fibre",
    "sodium": "Sodium",
    "protein": "Protein",
    "energy": "Energy",
    "cholesterol": "Cholesterol",
    "trans": "Trans Fat",
    "monounsaturated": "Mono Fat",
    "polyunsaturated": "Poly Fat",
    "potassium": "Potassium",
    "calcium": "Calcium",
}

# Canonical label → OFF key
OFF_KEY_MAP = {
    "Energy": "energy-kj",
    "Protein": "proteins",
    "Fat (Total)": "fat",
    "Fat (Saturated)": "fat-saturated",
    "Carbohydrate (Total)": "carbohydrates",
    "Carbohydrate (Sugars)": "carbohydrates-sugars",
    "Fibre": "fiber",
    "Sodium": "sodium",
    "Cholesterol": "cholesterol",
    "Trans Fat": "trans-fat",
    "Mono Fat": "monounsaturated-fat",
    "Poly Fat": "polyunsaturated-fat",
    "Potassium": "potassium",
    "Calcium": "calcium",
}

# --- NEW: canonical unit tables & helpers ------------------------------------
UNIT_NORMALISATION = {
    "kj": "kJ", "kjoules": "kJ",
    "kcal": "kcal",
    "g": "g",
    "mg": "mg",
    "μg": "mcg", "ug": "mcg", "mcg": "mcg",
    "ml": "ml",
    "l": "l",
}

# Default units for common nutrients when Woolies omits them
DEFAULT_NUTRIENT_UNITS = {
    "energy-kj": "kJ",
    "proteins": "g",
    "fat": "g",
    "fat-saturated": "g",
    "carbohydrates": "g",
    "carbohydrates-sugars": "g",
    "fiber": "g",
    "sodium": "mg",
    "cholesterol": "mg",
    "monounsaturated-fat": "g",
    "polyunsaturated-fat": "g",
    "trans-fat": "g",
    "potassium": "mg",
    "calcium": "mg",
}

CUP_PRICE_UNIT_NORMALISATION = {
    "100G": "100g",
    "100ML": "100ml",
    "1KG": "1kg",
    "1L": "1l",
}

def _canon_unit(unit: Optional[str]) -> Optional[str]:
    if not unit:
        return None
    u = unit.strip().lower()
    return UNIT_NORMALISATION.get(u, u)

def _canon_cup_unit(u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    return CUP_PRICE_UNIT_NORMALISATION.get(u.strip().upper(), u.strip().lower())



def normalize_label(raw: str) -> str:
    s = raw.strip().strip("–—- ").lower()
    for k, v in HUMAN_LABEL_MAP.items():
        if s.startswith(k):
            return v
    return raw.strip()


def off_key(label: str) -> str:
    return OFF_KEY_MAP.get(label, label.lower().replace(" ", "-"))


def parse_nip_attributes(nip_json_str: str) -> Dict[str, Dict[str, Any]]:
    nutrition: Dict[str, Dict[str, Any]] = {}
    if not nip_json_str:
        return nutrition

    try:
        data = json.loads(nip_json_str)
    except json.JSONDecodeError:
        return nutrition

    attrs = data.get("Attributes") or []
    for item in attrs:
        raw_name = item.get("Name", "") or ""
        value = item.get("Value", "") or ""

        canon = normalize_label(raw_name)
        key = off_key(canon)  # e.g., "carbohydrates-sugars"

        name_lc = raw_name.lower()
        if "per 100" in name_lc:
            bucket = "per_100"
        elif "per serve" in name_lc or "per serv" in name_lc:
            bucket = "per_serving"
        else:
            continue

        parsed = clean_numeric_unit(value)
        # Fill missing units from defaults when safe
        if parsed["unit"] is None:
            parsed["unit"] = DEFAULT_NUTRIENT_UNITS.get(key)

        node = nutrition.get(key) or {"label": canon, "per_100": None, "per_serving": None}
        node[bucket] = parsed
        nutrition[key] = node

    # prune empties
    for k in list(nutrition.keys()):
        if not nutrition[k].get("per_100") and not nutrition[k].get("per_serving"):
            nutrition.pop(k, None)
    return nutrition

CANON_MAP = {
    # Carbs
    "carbohydrate-quantity-per-100g---total---nip": "carbohydrates",
    "carbohydrate-quantity-per-serve---total---nip": "carbohydrates",

    # Fats
    "fat-quantity-per-100g---total---nip": "fat",
    "fat-quantity-per-serve---total---nip": "fat",
    "fat-saturated-quantity-per-100g---total---nip": "fat-saturated",
    "fat-saturated-quantity-per-serve---total---nip": "fat-saturated",
    "fat-trans-quantity-per-100g---total---nip": "trans-fat",
    "fat-trans-quantity-per-serve---total---nip": "trans-fat",
    "fat-polyunsaturated-quantity-per-100g---total---nip": "polyunsaturated-fat",
    "fat-polyunsaturated-quantity-per-serve---total---nip": "polyunsaturated-fat",
    "fat-monounsaturated-quantity-per-100g---total---nip": "monounsaturated-fat",
    "fat-monounsaturated-quantity-per-serve---total---nip": "monounsaturated-fat",

    # Protein
    "protein-quantity-per-100g---total---nip": "protein",
    "protein-quantity-per-serve---total---nip": "protein",
    "proteins": "protein",

    # Fibre + Sugar
    "fibre-quantity-per-100g---total---nip": "fiber",
    "fibre-quantity-per-serve---total---nip": "fiber",
    "sugars-quantity-per-100g---total---nip": "carbohydrates-sugars",
    "sugars-quantity-per-serve---total---nip": "carbohydrates-sugars",

    
    
}



def canonicalise_nutrition(nutrition: dict) -> dict:
    # Map verbose Woolies NIP labels → clean display names
    LABEL_CLEANUP_MAP = {
        "Fat Saturated Quantity Per 100g - Total - NIP": "Saturated Fat",
        "Fat Saturated Quantity Per Serve - Total - NIP": "Saturated Fat",
        "Fat Quantity Per 100g - Total - NIP": "Fat",
        "Fat Quantity Per Serve - Total - NIP": "Fat",
        "Carbohydrate Quantity Per 100g - Total - NIP": "Carbohydrate",
        "Carbohydrate Quantity Per Serve - Total - NIP": "Carbohydrate",
        "Protein Quantity Per 100g - Total - NIP": "Protein",
        "Protein Quantity Per Serve - Total - NIP": "Protein",
        "Sugars Quantity Per 100g - Total - NIP": "Sugars",
        "Sugars Quantity Per Serve - Total - NIP": "Sugars",
        "Fibre Quantity Per 100g - Total - NIP": "Fibre",
        "Fibre Quantity Per Serve - Total - NIP": "Fibre",
    }

    out = {}
    for key, node in nutrition.items():
        k = CANON_MAP.get(key, key)

        # Clean up label if it matches any of the verbose NIP patterns
        label = node.get("label")
        if label in LABEL_CLEANUP_MAP:
            label = LABEL_CLEANUP_MAP[label]

        if k not in out:
            out[k] = {"label": label, "per_100": None, "per_serving": None}

        # merge per_100
        if node.get("per_100"):
            out[k]["per_100"] = node["per_100"]

        # merge per_serving
        if node.get("per_serving"):
            out[k]["per_serving"] = node["per_serving"]

    # optional: derive energy-kcal
    if "energy-kj" in out and out["energy-kj"].get("per_100", {}).get("value") is not None:
        kj = float(out["energy-kj"]["per_100"]["value"])
        out["energy-kcal"] = {
            "label": "Energy (kcal)",
            "per_100": {"value": round(kj / 4.184), "unit": "kcal"},
            "per_serving": None,
        }

    # prune empty entries
    for k in list(out.keys()):
        if not out[k].get("per_100") and not out[k].get("per_serving"):
            out.pop(k, None)
    return out



# Parse allergens and claims

# --- NEW: parse allergens & claims -------------------------------------------
KNOWN_ALLERGENS = {"milk","egg","soy","wheat","gluten","peanut","tree_nut","fish","shellfish","sesame"}

def _normalise_tag(t: str) -> str:
    return " ".join(t.strip().split())

def split_allergens_and_claims(allergen_text: Optional[str], lifestyle_text: Optional[str]):
    """
    Returns:
      allergens_present: list[str]    (e.g., ["milk"])
      free_from_claims:  list[str]    (e.g., ["gluten free", "soy free"])
      dietary_tags:      list[str]    (from lifestyle block, normalised)
    """
    allergens_present: List[str] = []
    free_from_claims: List[str] = []

    tokens: List[str] = []
    if allergen_text:
        tokens += [t.strip() for t in str(allergen_text).replace(";", ",").split(",") if t.strip()]

    for t in tokens:
        tl = t.lower()
        # normalize spacings
        tl = _normalise_tag(tl)
        # map “contains milk/soy” → allergen present
        if "contains" in tl:
            for a in KNOWN_ALLERGENS:
                if a.replace("_"," ") in tl:
                    allergens_present.append(a)
        # map “x free”
        if "free" in tl:
            free_from_claims.append(tl)

    # lifestyle/dietary tags
    dietary_tags = []
    if lifestyle_text:
        dietary_tags = [_normalise_tag(s) for s in lifestyle_text.split(",") if s.strip()]

    # de-dup
    allergens_present = sorted(set(allergens_present))
    free_from_claims = sorted(set(free_from_claims))
    dietary_tags = sorted(set(dietary_tags))
    return allergens_present, free_from_claims, dietary_tags




# ============================================================
# Product normalization (one Woolies product card → universal dict)
# ============================================================
def guess_nutrition_basis(package_size: Optional[str], serving_unit: Optional[str]) -> str:
    """
    Decide per_100 basis. If it's a drink or serving unit is ml → 'per_100ml' else 'per_100g'.
    """
    if serving_unit and serving_unit.lower() in ("ml", "l"):
        return "per_100ml"
    if package_size and re.search(r"(?:\b|^)\d+(?:\.\d+)?\s*(?:ml|l)\b", package_size.lower()):
        return "per_100ml"
    return "per_100g"


def normalize_woolies_item(p: Dict[str, Any]) -> Dict[str, Any]:
    attr = p.get("AdditionalAttributes") or {}
    rating = p.get("Rating") or {}

    nip_raw = attr.get("nutritionalinformation")
    nutrition = parse_nip_attributes(nip_raw) if nip_raw else {}

    # --- Serving info
    serving_size = parse_serving_size(next(
        (a.get("Value") for a in (json.loads(nip_raw).get("Attributes", []) if nip_raw else [])
         if a.get("Name", "").lower().startswith("serving size")), None
    )) if nip_raw else {"value": None, "unit": None}

    servings_per_pack = next(
        (a.get("Value") for a in (json.loads(nip_raw).get("Attributes", []) if nip_raw else [])
         if a.get("Name", "").lower().startswith("servings per pack")), None
    )
    try:
        servings_per_pack = float(servings_per_pack) if servings_per_pack else None
    except ValueError:
        servings_per_pack = None

    # --- Basis
    nutrition_basis = guess_nutrition_basis(p.get("PackageSize"), serving_size["unit"])

    # --- Images (primary + gallery de-dup)
    gallery = list(dict.fromkeys((p.get("DetailsImagePaths") or [])))  # de-dup preserve order
    image_url = (
        p.get("LargeImageFile")
        or p.get("MediumImageFile")
        or p.get("SmallImageFile")
        or (gallery[0] if gallery else None)
    )

    # --- Cup price unit
    cup_price_unit = _canon_cup_unit(p.get("CupMeasure"))

    # --- Allergens / claims / lifestyle
    healthstarrating = attr.get("healthstarrating")
    allergens_text = attr.get("allergystatement") or attr.get("allergencontains")
    lifestyle_text = attr.get("lifestyleanddietarystatement") or ""
    allergens_present, free_from_claims, dietary_tags = split_allergens_and_claims(allergens_text, lifestyle_text)

    # --- Ratings (null if no votes)
    
    rating_avg = rating.get("Average")
    rating_cnt = rating.get("RatingCount")
    if isinstance(rating_cnt, (int, float)) and int(rating_cnt) == 0:
        rating_avg = None
        rating_cnt = None

    # --- Build item
    item = {
        "barcode": p.get("Barcode") or p.get("Stockcode"),
        "name": p.get("DisplayName") or p.get("Name"),
        "brand": p.get("Brand"),
        "description": strip_html(p.get("Description")),
        "size": p.get("PackageSize"),

        "price_current": p.get("InstorePrice") or p.get("Price"),
        "price_was": p.get("WasPrice"),
        "currency": DEFAULT_CURRENCY,
        "is_on_special": bool(p.get("IsOnSpecial") or p.get("InstoreIsOnSpecial")),
        "cup_price_value": p.get("CupPrice"),
        "cup_price_unit": cup_price_unit,

        "category": attr.get("sapcategoryname"),
        "subcategory": attr.get("sapsubcategoryname"),
        "country_of_origin": attr.get("countryoforigin"),

        "ingredients": attr.get("ingredients"),
        "allergens_raw": allergens_text,                 # keep raw for display
        "allergens_present": allergens_present,          # <- structured
        "free_from_claims": free_from_claims,            # <- structured

        "nutrition_basis": nutrition_basis,  # "per_100g" | "per_100ml"
        "serving_size_value": serving_size["value"],
        "serving_size_unit": serving_size["unit"],
        "servings_per_pack": servings_per_pack,

        "image_url": image_url,
        "product_url": f"https://www.woolworths.com.au/shop/productdetails/{p.get('Stockcode')}" if p.get("Stockcode") else None,

        "rating_average": rating_avg,
        "rating_count": rating_cnt,
        "health_star" : healthstarrating,

        "is_in_stock": p.get("IsInStock"),
        "availability_next_date": None,  # set below

        "primary_source": "woolworths",
        "external_ids": {"woolworths_stockcode": str(p.get("Stockcode")) if p.get("Stockcode") else None},
        "dietary_tags": dietary_tags,

        "nutrition": nutrition,
    }

    # Ensure allergens_present always exists
    # ensure presence
    item.setdefault("allergens_present", [])

    # canonical display labels for known nutrients
    _CANON_LABELS = {
        "energy-kj": "Energy",
        "energy-kcal": "Energy (kcal)",
        "fat": "Fat",
        "fat-saturated": "Saturated fat",
        "carbohydrates": "Carbohydrate",
        "carbohydrates-sugars": "Sugars",
        "protein": "Protein",
        "fiber": "Fibre",
        "sodium": "Sodium",
        "calcium": "Calcium",
    }

    # apply canonical labels + rounding policy
    for k, node in (item.get("nutrition") or {}).items():
        if not node: 
            continue
        if _CANON_LABELS.get(k):
            node["label"] = _CANON_LABELS[k]
        # rounding policy
        for bucket in ("per_100", "per_serving"):
            v = node.get(bucket)
            if v and v.get("value") is not None:
                if k in ("energy-kj", "energy-kcal"):
                    v["value"] = round(float(v["value"]))              # 0 dp
                else:
                    v["value"] = round(float(v["value"]), 2)           # 2 dp

    # Generate slugified version of dietary_tags for easy filtering/search
    item["dietary_tags_slugs"] = [
        t.lower().replace(" ", "-") for t in (item.get("dietary_tags") or [])
    ]

    # --- Availability ISO normalisation (UTC)
    if p.get("NextAvailabilityDate"):
        try:
            dt = datetime.fromisoformat(p["NextAvailabilityDate"].replace("Z", "+00:00"))
            item["availability_next_date"] = dt.isoformat()
        except Exception:
            item["availability_next_date"] = p.get("NextAvailabilityDate")

    # --- Back-calc missing per_100 from per_serving when possible
    sv = item.get("serving_size_value")
    su = item.get("serving_size_unit")
    if sv and su and nutrition:
        factor = None
        if su.lower() == "g":
            factor = 100.0 / float(sv)
        elif su.lower() == "ml":
            factor = 100.0 / float(sv)
        if factor:
            for key, node in nutrition.items():
                p100 = node.get("per_100")
                pserv = node.get("per_serving")
                if (not p100 or p100.get("value") is None) and pserv and pserv.get("value") is not None:
                    node["per_100"] = {
                        "value": round(float(pserv["value"]) * factor, 2),
                        "unit": pserv.get("unit") or DEFAULT_NUTRIENT_UNITS.get(key)
                    }

    # --- Prune empties
    nutrition = canonicalise_nutrition(nutrition)
    item["nutrition"] = nutrition

    # --- Prune empties and return
    item = {k: v for k, v in item.items() if v not in (None, "", [], {}, False) or k in ("is_on_special", "is_in_stock")}
    return item


# ============================================================
# Public: fetch_woolies(query) → [normalized items]
# ============================================================
def _get_with_retry(url: str, params: Dict[str, Any], retries: int = 3, timeout: int = 20) -> Dict[str, Any]:
    last_exc = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ReadTimeout as e:
            last_exc = e
            if attempt < retries - 1:
                time.sleep(0.8 * (attempt + 1))
                continue
            raise
        except requests.RequestException as e:
            last_exc = e
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise
    if last_exc:
        raise last_exc
    return {}


def fetch_woolies(query: str) -> List[Dict[str, Any]]:
    """
    Search Woolworths for `query` and return normalized product dicts.
    Fully source-agnostic fields; ready to upsert into your Product model.
    """
    cache_key = f"woolies:{query.lower()}"
    if _HAS_DJANGO_CACHE:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    data = _get_with_retry(WOLLIES_SEARCH_URL, {"searchTerm": query}, retries=3, timeout=20)
    results: List[Dict[str, Any]] = []

    for bucket in data.get("Products", []) or []:
        for p in bucket.get("Products", []) or []:
            norm = normalize_woolies_item(p)
            if norm.get("name"):
                results.append(norm)

    # ---  Step 6: de-duplicate by barcode / stockcode before caching -------------
    seen: set[str] = set()
    deduped: list[dict] = []
    for r in results:
        key = r.get("barcode") or (r.get("external_ids", {}) or {}).get("woolworths_stockcode")
        if not key:
            continue  # skip totally unidentified items
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    if _HAS_DJANGO_CACHE:
        cache.set(cache_key, deduped, CACHE_TTL_S)
    return deduped


# ============================================================
# Optional: Django ingestion helpers
# ============================================================
def ingest_woolies_normalized_item(item: Dict[str, Any]) -> Optional[Any]:
    """
    Upsert a normalized item into Django models.
    Assumes:
      - Product model with fields from your latest schema
      - Nutrient model with unique name + unit (or just name)
      - ProductNutrient with amounts per 100 basis and per serving
    """
    try:
        from apps.core.models.product import Product  # type: ignore
        from apps.core.models.nutrients import Nutrient  # type: ignore
        from apps.core.models.product_nutrient import ProductNutrient  # type: ignore
        from django.utils import timezone  # type: ignore
    except Exception:
        # Not running inside Django context
        return None

    barcode = item.get("barcode")
    defaults = {k: v for k, v in item.items() if k not in ("nutrition",)}
    defaults["last_enriched_at"] = timezone.now()

    lookup = {"barcode": barcode} if barcode else None
    if not lookup:
        stockcode = (item.get("external_ids") or {}).get("woolworths_stockcode")
        if not stockcode:
            return None
        lookup = {"barcode": f"WW-STOCK-{stockcode}"}

    product, _created = Product.objects.update_or_create(**lookup, defaults=defaults)

    nip = item.get("nutrition") or {}
    for key, node in nip.items():
        label = node.get("label")
        if not label:
            continue
        nutrient, _ = Nutrient.objects.get_or_create(name=label, defaults={"unit": (node.get("per_100") or {}).get("unit")})

        per100 = (node.get("per_100") or {}).get("value")
        per_serv = (node.get("per_serving") or {}).get("value")
        if per100 is None and per_serv is None:
            continue  # skip empty rows

        ProductNutrient.objects.update_or_create(
            product=product,
            nutrient=nutrient,
            defaults={
                "amount_per_100g": float(per100) if per100 is not None else 0.0,
                "amount_per_serving": float(per_serv) if per_serv is not None else None,
            },
        )
    return product


def ingest_woolies_search(query: str, limit: int = 50) -> List[Any]:
    """
    Fetch and ingest top N search results into Django. Returns list of Product instances.
    """
    items = fetch_woolies(query)
    out = []
    for item in items[:limit]:
        obj = ingest_woolies_normalized_item(item)
        if obj is not None:
            out.append(obj)
    return out


# ============================================================
# Local test harness
# ============================================================
if __name__ == "__main__":
    import json

    TEST_TERMS = ["Macro Chicken Breast Fillets Free Range", "bread", "yogurt"]

    for term in TEST_TERMS:
        print(f"\n Searching Woolies for: {term}\n{'-'*70}")
        try:
            items = fetch_woolies(term)
        except Exception as e:
            print(" Request failed:", e)
            continue

        # Print the raw JSON object (normalized output)
        for i, p in enumerate(items[:3]):  # limit to 3 per term
            print(f"\n🧾 Result {i+1}: {p.get('name')}")
            print(json.dumps(p, indent=2, ensure_ascii=False))
            print("-" * 70)
