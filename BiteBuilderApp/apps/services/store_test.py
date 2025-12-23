import requests
import json

def test_woolworths_store_locator(postcode="2168"):
    url = "https://www.woolworths.com.au/apis/ui/StoreLocator/Stores"
    params = {
        "Max": 3,
        "Division": "SUPERMARKETS,EG,AMPOL",
        "Facility": "",
        "postcode": postcode,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.woolworths.com.au/",
        "Origin": "https://www.woolworths.com.au",
        "Accept-Language": "en-AU,en;q=0.9",
    }

    print(f"🔎 Fetching Woolworths stores near postcode {postcode}...")
    response = requests.get(url, headers=headers, params=params)

    print(f"📡 Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data.get('Stores', []))} stores")
        print(json.dumps(data.get("Stores", [])[:3], indent=2))
    else:
        print("❌ Request failed:")
        print(response.text[:500])

if __name__ == "__main__":
    test_woolworths_store_locator("2168")
