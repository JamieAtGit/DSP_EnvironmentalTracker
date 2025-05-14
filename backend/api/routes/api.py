from flask import request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin

from backend.scrapers.amazon.scrape_amazon_titles import scrape_amazon_product_page, haversine, origin_hubs, uk_hub
import pgeocode

#app = Flask(__name__)
#CORS(app)

# Helper function to determine transport mode based on distance
def determine_transport_mode(distance_km):
    if distance_km < 1500:
        return "Truck", 0.12  # 120g per tonne-km
    elif distance_km < 6000:
        return "Ship", 0.02   # 20g per tonne-km
    else:
        return "Air", 0.5     # 500g per tonne-km
    
def calculate_eco_score(carbon_kg, recyclability, distance_km, weight_kg):
    carbon_score = max(0, 10 - carbon_kg * 5)
    weight_score = max(0, 10 - weight_kg * 2)
    distance_score = max(0, 10 - distance_km / 1000)
    recycle_score = {
        "Low": 2,
        "Medium": 6,
        "High": 10
    }.get(recyclability or "Medium", 5)

    return {
        True: "A+",
        distance_score >= 8: "A",
        distance_score >= 6.5: "B",
        distance_score >= 5: "C",
        distance_score >= 3.5: "D"
    }.get(True, "F")
    

def register_estimate_route(app):
    @app.route("/estimate_emissions", methods=["POST", "OPTIONS"])
    @cross_origin(origin="https://dsp-environmentaltracker.onrender.com", supports_credentials=True)
    def estimate():
        if request.method == "OPTIONS":
            return '', 204
        
        data = request.get_json()
        url = data.get("amazon_url")
        postcode = data.get("postcode")
        include_packaging = data.get("include_packaging", True)
        override_mode = data.get("override_transport_mode")

        if not url or not postcode:
            return jsonify({'error': 'Missing URL or postcode'}), 400

        geo = pgeocode.Nominatim('gb')
        location = geo.query_postal_code(postcode)
        if location.empty or location.latitude is None:
            return jsonify({'error': 'Invalid postcode'}), 400

        user_lat, user_lon = location.latitude, location.longitude
        product = scrape_amazon_product_page(url)
        if not product:
            return jsonify({'error': 'Could not fetch product'}), 500

        origin = origin_hubs.get(product['brand_estimated_origin'], uk_hub)
        distance = haversine(origin['lat'], origin['lon'], user_lat, user_lon)
        origin_distance = round(distance, 1)
        uk_distance = round(haversine(uk_hub['lat'], uk_hub['lon'], user_lat, user_lon), 1)

        raw_weight = product['estimated_weight_kg']
        final_weight = raw_weight * 1.05 if include_packaging else raw_weight

        transport_mode, emission_factor = determine_transport_mode(distance)
        modes = { "Air": 0.5, "Ship": 0.03, "Truck": 0.15 }

        if override_mode in modes:
            transport_mode = override_mode
            emission_factor = modes[override_mode]

        carbon_kg = round(final_weight * emission_factor * (distance / 1000), 2)
        eco_score = calculate_eco_score(carbon_kg, product.get("recyclability"), origin_distance, final_weight)
        confidence = product.get("confidence", "Estimated")

        return jsonify({
            "title": product.get("title"),
            "data": {
                "attributes": {
                    "carbon_kg": carbon_kg,
                    "weight_kg": round(final_weight, 2),
                    "raw_product_weight_kg": round(raw_weight, 2),
                    "origin": product['brand_estimated_origin'],
                    "intl_distance_km": origin_distance,
                    "uk_distance_km": uk_distance,
                    "distance_from_origin_km": origin_distance,
                    "distance_from_uk_hub_km": uk_distance,
                    "dimensions_cm": product.get("dimensions_cm"),
                    "material_type": product.get("material_type"),
                    "transport_mode": transport_mode,
                    "emission_factors": modes,
                    "eco_score_ml": eco_score,
                    "recyclability": product.get("recyclability"),
                    "confidence": confidence,
                    "origin_source": product.get("origin_source", "brand_db"),
                    "trees_to_offset": round(carbon_kg / 20, 1),
                }
            }
        })