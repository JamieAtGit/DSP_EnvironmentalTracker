import json
import os

# === CONFIG ===
BRAND_ORIGIN_JSON = os.path.join(os.path.dirname(__file__), "json", "brand_origin_data.json")

# === Load brand origin data ===
def load_brand_origin_data():
    if not os.path.exists(BRAND_ORIGIN_JSON):
        return {}
    with open(BRAND_ORIGIN_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

# === Save updated brand origin data ===
def save_brand_origin_data(data):
    with open(BRAND_ORIGIN_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Get brand origin ===
def get_brand_origin(brand):
    brand = brand.lower().strip()
    data = load_brand_origin_data()
    return data.get(brand, {"country": "Unknown", "city": "Unknown"})

# === Update or add brand origin ===
def update_brand_origin(brand, country, city="Unknown"):
    brand = brand.lower().strip()
    data = load_brand_origin_data()
    data[brand] = {"country": country.title(), "city": city.title()}
    save_brand_origin_data(data)
