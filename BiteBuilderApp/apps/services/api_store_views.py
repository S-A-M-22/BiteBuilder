from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests, math
from requests.exceptions import ReadTimeout, ConnectionError

@api_view(["GET"])
def api_stores_nearby(request):
    """
    Fetch nearby Woolworths Supermarkets only (no EG or Ampol).
    Query params:
      - postcode (required)
      - max (optional, default 5)
    """
    postcode = request.GET.get("postcode")
    max_results = request.GET.get("max", 5)

    if not postcode:
        return Response({"error": "Missing postcode"}, status=400)

    try:
        # Woolworths official Store Locator endpoint
        r = requests.get(
            "https://www.woolworths.com.au/apis/ui/StoreLocator/Stores",
            params={
                "Max": max_results,
                "Division": "SUPERMARKETS",  # 🔹 Woolies only
                "Facility": "",
                "postcode": postcode,
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.woolworths.com.au/",
                "Origin": "https://www.woolworths.com.au",
            },
            timeout=8,
        )
        r.raise_for_status()
        data = r.json().get("Stores", [])
    except ReadTimeout:
        return Response({"error": "Woolworths API timed out."}, status=504)
    except ConnectionError:
        return Response({"error": "Unable to reach Woolworths API."}, status=502)
    except Exception as e:
        return Response({"error": f"Request failed: {str(e)}"}, status=500)

    # build clean response
    stores = []
    for s in data:
        if s.get("Division") == "SUPERMARKETS":
            stores.append({
                "id": s.get("StoreNo"),
                "name": s.get("Name"),
                "address": s.get("AddressLine1"),
                "suburb": s.get("Suburb"),
                "state": s.get("State"),
                "postcode": s.get("Postcode"),
                "latitude": s.get("Latitude"),
                "longitude": s.get("Longitude"),
                "is_open": s.get("IsOpen"),
                "today_hours": s.get("TradingHours", [{}])[0].get("OpenHour") if s.get("TradingHours") else None,
            })

    return Response(stores)
