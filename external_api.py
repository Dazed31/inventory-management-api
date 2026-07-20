import requests

# OpenFoodFacts requires a custom User-Agent for all requests
USER_AGENT = "InventoryManagementApp/1.0 (student@example.com)"
BASE_URL = "https://world.openfoodfacts.org"


def fetch_product_by_barcode(barcode):
    url = f"{BASE_URL}/api/v3/product/{barcode}.json"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to reach OpenFoodFacts API: {str(e)}"}

    data = response.json()

    if data.get("status") != 1:
        return None

    return data.get("product", {})


def fetch_product_by_name(name):
    url = f"{BASE_URL}/cgi/search.pl"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to reach OpenFoodFacts API: {str(e)}"}

    data = response.json()
    products = data.get("products", [])

    if not products:
        return None

    return [
        {
            "product_name": p.get("product_name", "Unknown"),
            "brands": p.get("brands", ""),
            "barcode": p.get("code", ""),
            "ingredients_text": p.get("ingredients_text", "")
        }
        for p in products
    ]