import time, uuid, hmac, hashlib, base64, urllib.parse, json, requests
from django.conf import settings

NLP_URL = "https://platform.fatsecret.com/rest/natural-language-processing/v1"

def _generate_signature(base_url: str, http_method: str, params: dict) -> str:
    params_sorted = dict(sorted(params.items()))
    param_str = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params_sorted.items())
    base_str = f"{http_method.upper()}&{urllib.parse.quote(base_url, safe='')}&{urllib.parse.quote(param_str, safe='')}"
    key = f"{settings.FATSECRET_CONSUMER_SECRET}&"
    digest = hmac.new(key.encode("utf-8"), base_str.encode("utf-8"), hashlib.sha1).digest()
    return base64.b64encode(digest).decode("utf-8")


def _oauth_header(http_method: str, base_url: str) -> dict:
    oauth_params = {
        "oauth_consumer_key": settings.FATSECRET_CONSUMER_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0",
    }
    oauth_params["oauth_signature"] = _generate_signature(base_url, http_method, oauth_params)
    header = "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(v)}"' for k, v in oauth_params.items())
    return {"Authorization": header}


def analyze_meal_text(user_input: str, include_food_data=True, region="US", language="en"):
    """
    FatSecret NLP v1 (OAuth1) — send JSON body, sign request, Authorization header.
    """
    headers = {
        **_oauth_header("POST", NLP_URL),
        "Content-Type": "application/json",
    }
    payload = {
        "user_input": user_input,
        "include_food_data": include_food_data,
        "region": region,
        "language": language,
        "format": "json",
    }

    print("[INFO] POST", NLP_URL)
    print("[INFO] Payload:", payload)
    r = requests.post(NLP_URL, headers=headers, data=json.dumps(payload), timeout=20)
    print("[INFO] Status:", r.status_code)
    print("[INFO] Response:", r.text[:400])

    try:
        data = r.json()
        if "error" in data:
            print("[WARNING] API error:", data["error"])
        else:
            print("[SUCCESS] NLP parse OK")
        return data
    except ValueError:
        print("[ERROR] Non-JSON response:", r.text[:400])
        return None
