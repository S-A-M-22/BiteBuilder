# ===============================================
# apps/core/services/fatsecret_oauth2_client.py
# ===============================================
"""
FatSecret OAuth 2.0 Client — Tested for Premier Free / Paid tiers

Features:
- OAuth2 client_credentials flow
- Token caching and auto-refresh
- Authorized GET wrapper with safe JSON parsing
- Full debug logging of URL, status, and payload
- Compatible with both US-only and regional datasets
"""

import os, sys, time, requests
from django.conf import settings
from django.core.cache import cache


# --------------------------------------------------
# ⚙️ Bootstrap Django if run standalone
# --------------------------------------------------
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BiteBuilderApp.settings")
    import django
    django.setup()


# --------------------------------------------------
# 🔑 Token Management
# --------------------------------------------------
def _fetch_new_token() -> dict:
    """
    Request a new OAuth2 access token from FatSecret.
    Returns: dict with {access_token, expires_in, token_type, scope}
    """
    data = {
        "grant_type": "client_credentials",
        # Request full scopes (server will issue subset if not entitled)
        "scope": "basic premier nlp",
    }
    auth = (settings.FATSECRET2_CLIENT_ID, settings.FATSECRET2_CLIENT_SECRET)

    print(" Requesting new token from FatSecret...")
    r = requests.post(settings.FATSECRET2_TOKEN_URL, data=data, auth=auth, timeout=10)
    print("Status:", r.status_code)
    print("Response:", r.text)

    r.raise_for_status()
    token = r.json()
    token["fetched_at"] = time.time()

    # Cache token (~1h default, FatSecret usually returns 86400s)
    cache.set("fatsecret2_token", token, timeout=token.get("expires_in", 3500))
    return token


def _get_cached_token() -> str:
    """Retrieve a valid access token (fetch new if expired)."""
    token = cache.get("fatsecret2_token")
    if not token:
        token = _fetch_new_token()
    return token["access_token"]


# --------------------------------------------------
# 🌐 Authorized GET
# --------------------------------------------------
def _authorized_get(endpoint: str, params: dict | None = None):
    """
    Perform an authorized GET request with the current access token.
    Returns parsed JSON or error dict if non-JSON.
    """
    access_token = _get_cached_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = endpoint if endpoint.startswith("http") else f"https://platform.fatsecret.com/rest/{endpoint.lstrip('/')}"

    r = requests.get(url, headers=headers, params=params, timeout=15)
    print(" URL:", r.url)
    print(" Status:", r.status_code)

    if r.status_code == 401:  # expired token
        access_token = _fetch_new_token()["access_token"]
        headers["Authorization"] = f"Bearer {access_token}"
        r = requests.get(url, headers=headers, params=params, timeout=15)

    print(" Response preview:", r.text[:300])

    try:
        return r.json()
    except ValueError:
        print(" Response was not JSON — likely HTML or empty error page.")
        return {"error": {"message": "Non-JSON response", "body": r.text}}


# --------------------------------------------------
# 🔎 High-Level API Functions
# --------------------------------------------------
def find_food_by_barcode(barcode: str):
    """
    Look up a food by GTIN-13 barcode.
    Works for US data on Premier Free; AU data requires paid localization.
    """
    url = "https://platform.fatsecret.com/rest/server.api"
    params = {
        "method": "food.find_id_for_barcode.v2",
        "barcode": barcode,
        "region": settings.FATSECRET2_REGION.strip(),
        "format": "json",
    }
    print(" Payload params:", params)
    data = _authorized_get(url, params)

    # Optional: fallback for AU→US if 211
    if "error" in data and data["error"].get("code") == 211 and params["region"] != "US":
        print(" No match for region", params["region"], "— retrying with US dataset...")
        params["region"] = "US"
        data = _authorized_get(url, params)
    return data


def get_food(food_id: int):
    """Retrieve full nutrient data by food_id."""
    url = "https://platform.fatsecret.com/rest/server.api"
    params = {"method": "food.get.v5", "food_id": food_id, "format": "json"}
    return _authorized_get(url, params)


def search_foods(term: str, max_results: int = 10):
    """Search for foods by keyword."""
    url = "https://platform.fatsecret.com/rest/server.api"
    params = {"method": "foods.search.v4", "search_expression": term, "format": "json", "max_results": max_results}
    return _authorized_get(url, params)


# --------------------------------------------------
# 🧠 Natural Language Processing API
# --------------------------------------------------
def analyze_meal_text(user_input: str, include_food_data=True, region="US", language="en"):
    """
    FatSecret NLP v1 — parses meal descriptions into structured food/nutrient data.
    Requires OAuth2 token with 'nlp' scope.
    """
    url = "https://platform.fatsecret.com/rest/natural-language-processing/v1"
    headers = {
        "Authorization": f"Bearer {_get_cached_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "user_input": user_input,
        "include_food_data": include_food_data,
        "region": region,
        "language": language,
    }

    print(" POST", url)
    print(" Headers", headers)
    print(" Payload", payload)

    r = requests.post(url, headers=headers, json=payload, timeout=20)
    print(" Status:", r.status_code)
    print(" Response preview:", r.text[:400])

    if r.status_code == 401:
        print(" Token expired, refreshing...")
        headers["Authorization"] = f"Bearer {_fetch_new_token()['access_token']}"
        r = requests.post(url, headers=headers, json=payload, timeout=20)

    try:
        data = r.json()
        if "error" in data:
            print(" API Error:", data["error"])
        else:
            print(" NLP result OK")
        return data
    except ValueError:
        print(" Non-JSON response:", r.text[:400])
        return None


# --------------------------------------------------
# 🧪 Self-Test
# --------------------------------------------------
if __name__ == "__main__":
    res = analyze_meal_text("For breakfast I ate a slice of toast with butter and a cappuccino")
    for f in res.get("food_response", []):
        print(f"{f['food_entry_name']}: {f['eaten']['total_nutritional_content']}")
