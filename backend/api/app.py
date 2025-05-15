from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import joblib
import sys
import os
import os

from uuid import uuid4
from scraper_worker import load_queue, save_queue



BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

model_dir = os.path.join(BASE_DIR, "backend", "ml", "models")
encoders_dir = os.path.join(BASE_DIR, "backend", "ml", "encoders")

import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.api.routes.auth import register_routes
from backend.api.routes.api import calculate_eco_score


import pandas as pd
from backend.scrapers.amazon.scrape_amazon_titles import (
    scrape_amazon_product_page,
    estimate_origin_country,
    resolve_brand_origin,
    save_brand_locations
)
from backend.scrapers.amazon.scrape_amazon_titles import haversine, origin_hubs, uk_hub

import csv
import re
import numpy as np
import pgeocode

# === Load Flask ===
#   app = Flask(__name__)
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    static_url_path="/static"
)
app.secret_key = "super-secret-key"


from flask_cors import CORS

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://www.amazon.co.uk",
    "https://www.amazon.com",
    "chrome-extension://lohejhmgkkmcdhnomjcpgfbeoabjncmp"
])




register_routes(app)



SUBMISSION_FILE = "submitted_predictions.json"


@app.route("/admin/submissions")
def get_submissions():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    if not os.path.exists(SUBMISSION_FILE):
        return jsonify([])

    with open(SUBMISSION_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))



@app.route("/admin/update", methods=["POST"])
def update_submission():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    item = request.json
    with open(SUBMISSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for i, row in enumerate(data):
        if row["title"] == item["title"]:
            data[i] = item
            break
    with open(SUBMISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "success"})



def log_submission(product):
    path = "submitted_predictions.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(product)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
def load_material_co2_data():
    try:
        import pandas as pd
        df = pd.read_csv(os.path.join(model_dir, "defra_material_intensity.csv")) 
        return {str(row["material"]).lower(): float(row["co2_per_kg"]) for _, row in df.iterrows()}
    except Exception as e:
        print(f"⚠️ Could not load CO₂ map: {e}")
        return {}

material_co2_map = load_material_co2_data()


@app.route("/predict", methods=["POST"])
def predict_eco_score():
    
    print("📩 /predict endpoint was hit via POST")  # debug
    try:
        data = request.get_json()
        product = data  # ensure it's always defined
        material = normalize_feature(data.get("material"), "Other")
        weight = float(data.get("weight") or 0.0)
        # Estimate default transport from distance if none provided
        user_transport = data.get("transport")
        origin_km = float(product.get("distance_origin_to_uk", 0) or 0)

        # Heuristic fallback: choose mode by distance
        def guess_transport_by_distance(km):
            if km > 7000:
                return "Ship"
            elif km > 2000:
                return "Air"
            else:
                return "Land"

        # === Determine transport mode based on distance (default + override)
        override_transport = normalize_feature(data.get("override_transport_mode"), None)

        def determine_transport_mode(distance_km):
            if distance_km < 1500:
                return "Truck", 0.15
            elif distance_km < 6000:
                return "Ship", 0.03
            else:
                return "Air", 0.5
            
        origin_distance_km = float(data.get("distance_origin_to_uk") or 0)


        default_mode, default_emission_factor = determine_transport_mode(origin_distance_km)

        if override_transport in ["Truck", "Ship", "Air"]:
            transport = override_transport
            print(f"🚛 User override mode: {transport}")
        else:
            transport = default_mode
            print(f"📦 Default transport mode applied: {transport}")

        print(f"🚛 Final transport used: {transport} (user selected: {user_transport})")

        recyclability = normalize_feature(data.get("recyclability"), "Medium")
        origin = normalize_feature(data.get("origin"), "Other")

        # === Encode features
        material_encoded = safe_encode(material, material_encoder, "Other")
        transport_encoded = safe_encode(transport, transport_encoder, "Land")
        recycle_encoded = safe_encode(recyclability, recycle_encoder, "Medium")
        origin_encoded = safe_encode(origin, origin_encoder, "Other")

        # === Bin weight (for 6th feature)
        def bin_weight(w):
            if w < 0.5:
                return 0
            elif w < 2:
                return 1
            elif w < 10:
                return 2
            else:
                return 3

        weight_bin_encoded = bin_weight(weight)

        weight_log = np.log1p(weight)

        # === Prepare input for model
        X = [[
            material_encoded,
            transport_encoded,
            recycle_encoded,
            origin_encoded,
            weight_log,
            weight_bin_encoded
        ]]
        
        prediction = model.predict(X)
        decoded_score = label_encoder.inverse_transform([prediction[0]])[0]

        print("🧠 Predicted Label:", decoded_score)
        
        confidence = 0.0
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)
            print("🧪 predict_proba output:", proba)
            print("🎯 Raw predict_proba values:", proba[0])  # <=== ADD THIS HERE

            best_index = int(np.argmax(proba[0]))
            best_label = label_encoder.inverse_transform([best_index])[0]
            confidence = round(float(proba[0][best_index]) * 100, 1)

            print(f"🧠 Most confident class: {best_label} with {confidence}%")

                
        # === Feature Importance (optional)
        global_importance = model.feature_importances_
        local_impact = {
            "material": to_python_type(material_encoded * global_importance[0]),
            "weight": to_python_type(weight * global_importance[1]),
            "transport": to_python_type(transport_encoded * global_importance[2]),
            "recyclability": to_python_type(recycle_encoded * global_importance[3]),
            "origin": to_python_type(origin_encoded * global_importance[4]),
            "weight_bin": to_python_type(weight_bin_encoded * global_importance[5]),
        }

        # === Log the prediction
        log_submission({
            "title": data.get("title", "Manual Submission"),
            "raw_input": {
                "material": material,
                "weight": weight,
                "transport": transport,
                "recyclability": recyclability,
                "origin": origin
            },
            "predicted_label": decoded_score,
            "confidence": f"{confidence}%"
        })

        # === Return JSON response
        return jsonify({
            "predicted_label": decoded_score,
            "confidence": f"{confidence}%",
            "raw_input": {
                "material": material,
                "weight": weight,
                "transport": transport,
                "recyclability": recyclability,
                "origin": origin
            },
            "encoded_input": {
                "material": to_python_type(material_encoded),
                "weight": to_python_type(weight),
                "transport": to_python_type(transport_encoded),
                "recyclability": to_python_type(recycle_encoded),
                "origin": to_python_type(origin_encoded),
                "weight_bin": to_python_type(weight_bin_encoded)
            },
            "feature_impact": local_impact
        })

    except Exception as e:
        print(f"❌ Error in /predict: {e}")
        return jsonify({"error": str(e)}), 500


# === Load Model and Encoders ===

model = joblib.load(os.path.join(model_dir, "eco_model.pkl"))
material_encoder = joblib.load("backend/ml/ml_model/encoders/material_encoder.pkl")

print("🧩 Loaded material encoder classes:", material_encoder.classes_)

transport_encoder = joblib.load(os.path.join(encoders_dir, "transport_encoder.pkl"))
recycle_encoder = joblib.load(os.path.join(encoders_dir, "recycle_encoder.pkl"))
label_encoder = joblib.load(os.path.join(encoders_dir, "label_encoder.pkl"))
origin_encoder = joblib.load(os.path.join(encoders_dir, "origin_encoder.pkl"))
valid_scores = list(label_encoder.classes_)
print("✅ Loaded label classes:", valid_scores)


@app.route("/all-model-metrics", methods=["GET"])
def get_all_model_metrics():
    try:
        with open(os.path.join(model_dir, "metrics.json"), "r") as f1, open(os.path.join(model_dir, "xgb_metrics.json"), "r") as f2:
            return jsonify({
                "random_forest": json.load(f1),
                "xgboost": json.load(f2)
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/model-metrics", methods=["GET"])
def get_model_metrics():
    try:
        with open(os.path.join(model_dir, "ml_model/metrics.json", "r", encoding="utf-8")) as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# === Load CO2 Map ===
def load_material_co2_data():
    try:
        df = pd.read_csv(os.path.join(model_dir, "defra_material_intensity.csv"))
        return dict(zip(df["material"], df["co2_per_kg"]))
    except Exception as e:
        print(f"⚠️ Could not load DEFRA data: {e}")
        return {}

material_co2_map = load_material_co2_data()

# === Helpers ===
def normalize_feature(value, default):
    clean = str(value or default).strip().title()
    return default if clean.lower() == "unknown" else clean

def safe_encode(value, encoder, default):
    value = normalize_feature(value, default)
    if value not in encoder.classes_:
        print(f"⚠️ '{value}' not in encoder classes. Defaulting to '{default}'.")
        value = default
    return encoder.transform([value])[0]

@app.route("/api/feature-importance")
def get_feature_importance():
    try:
        importances = model.feature_importances_
        features = ["material", "weight", "transport", "recyclability", "origin"]
        data = [{"feature": f, "importance": round(i * 100, 2)} for f, i in zip(features, importances)]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def to_python_type(obj):
    import numpy as np
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    return obj


# === Fuzzy Matching Helpers ===
def fuzzy_match_material(text):
    material_keywords = {
        "Plastic": ["plastic", "plastics"],
        "Glass": ["glass"],
        "Aluminium": ["aluminium", "aluminum"],
        "Steel": ["steel"],
        "Paper": ["paper", "papers"],
        "Cardboard": ["cardboard", "corrugated"],
        "Leather": ["leather", "buffalo", "veg tan"],
        "Wood": ["wood", "timber"],
        "Foam": ["foam", "polyurethane"],
    }

    text = str(text or "").lower()
    for label, keywords in material_keywords.items():
        if any(keyword in text for keyword in keywords):
            return label
    return "Other"

    material_lower = material.lower()
    for clean, keywords in material_keywords.items():
        if any(keyword in material_lower for keyword in keywords):
            return clean
    return material

def fuzzy_match_origin(origin):
    origin_keywords = {
        "China": ["china"],
        "UK": ["uk", "united kingdom"],
        "USA": ["usa", "united states", "america"],
        "Germany": ["germany"],
        "France": ["france"],
        "Italy": ["italy"],
    }

    origin_lower = origin.lower()
    for clean, keywords in origin_keywords.items():
        if any(keyword in origin_lower for keyword in keywords):
            return clean
    return origin

@app.route("/api/eco-data", methods=["GET"])
def fetch_eco_dataset():
    try:
        dataset_path = os.path.join(BASE_DIR, "common", "data", "csv", "eco_dataset.csv")
        #print("📁 Trying to read:", dataset_path)
        df = pd.read_csv(dataset_path)
        #print("✅ Loaded:", df.shape)
        #print("🧪 Columns:", df.columns.tolist())
        df = df.dropna(subset=["material", "true_eco_score", "co2_emissions"])
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print(f"❌ Failed to return eco dataset: {e}")
        return jsonify({"error": str(e)}), 500




@app.route("/insights", methods=["GET"])
def insights_dashboard():
    try:
        # Load the logged data
        dataset_path = os.path.join(BASE_DIR, "common", "data", "csv", "eco_dataset.csv")
        df = pd.read_csv(dataset_path)
        print("🔍 Dataset path:", dataset_path)
        print("✅ Exists?", os.path.exists(dataset_path))


        df = df.dropna(subset=["material", "true_eco_score", "co2_emissions"])  # Clean

        # Keep only the needed fields
        insights = df[["material", "true_eco_score", "co2_emissions"]]
        insights = insights.head(1000)  # Limit for frontend performance

        return jsonify(insights.to_dict(orient="records"))
    except Exception as e:
        print(f"❌ Failed to serve insights: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/feedback", methods=["POST"])
def save_feedback():
    try:
        data = request.get_json()
        feedback_dir = os.path.join("ml_model", "user_feedback.json")
        print("Received feedback:", data)
        # Append to file
        import json
        existing = []
        if os.path.exists(feedback_dir):
            with open(feedback_dir, "r") as f:
                existing = json.load(f)

        existing.append(data)

        with open(feedback_dir, "w") as f:
            json.dump(existing, f, indent=2)

        return jsonify({"message": "✅ Feedback saved!"}), 200

    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/estimate_emissions", methods=["POST"])
@app.route("/estimate_emissions", methods=["POST"])
def estimate_emissions():
    print("🔔 Route hit: /estimate_emissions")

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON in request"}), 400

    try:
        url = data.get("amazon_url")
        postcode = data.get("postcode")
        include_packaging = data.get("include_packaging", True)
        override_mode = data.get("override_transport_mode")

        # Validate inputs
        if not url or not postcode:
            return jsonify({"error": "Missing URL or postcode"}), 400

        # Scrape product
        from backend.scrapers.amazon.scrape_amazon_titles import scrape_amazon_product_page, haversine, origin_hubs, uk_hub
        product = scrape_amazon_product_page(url)
        if not product:
            return jsonify({"error": "Could not fetch product"}), 500

        # Get user coordinates from postcode
        import pgeocode
        geo = pgeocode.Nominatim("gb")
        location = geo.query_postal_code(postcode)
        if location.empty or location.latitude is None:
            return jsonify({"error": "Invalid postcode"}), 400

        user_lat, user_lon = location.latitude, location.longitude

        # Get origin coordinates
        origin_country = product.get("brand_estimated_origin", "Other")
        origin_coords = origin_hubs.get(origin_country, uk_hub)

        # Distance calculations
        origin_distance_km = round(haversine(origin_coords["lat"], origin_coords["lon"], user_lat, user_lon), 1)
        uk_distance_km = round(haversine(uk_hub["lat"], uk_hub["lon"], user_lat, user_lon), 1)

        print(f"🌍 Distances → origin: {origin_distance_km} km | UK hub: {uk_distance_km} km")

        # Use weight
        raw_weight = product.get("raw_product_weight_kg") or 0.5
        weight = float(raw_weight)
        if include_packaging:
            weight *= 1.05

        # Transport mode logic
        def determine_transport_mode(distance_km):
            if distance_km < 1500:
                return "Truck", 0.12
            elif distance_km < 6000:
                return "Ship", 0.02
            else:
                return "Air", 0.5

        default_mode, default_emission_factor = determine_transport_mode(origin_distance_km)

        modes = {
            "Air": 0.5,
            "Ship": 0.03,
            "Truck": 0.15
        }

        if override_mode in modes:
            transport_mode = override_mode
            emission_factor = modes[override_mode]
            print(f"🚚 Override transport mode used: {transport_mode}")
        else:
            transport_mode = default_mode
            emission_factor = default_emission_factor
            print(f"📦 Auto-detected transport mode used: {transport_mode}")

        carbon_kg = round(weight * emission_factor * (origin_distance_km / 1000), 2)
        
        eco_score_rule = calculate_eco_score(
            carbon_kg,
            product.get("recyclability", "Medium"),
            origin_distance_km,
            weight
        )


        # === ML Prediction for Eco Score
        try:
            material = product.get("material_type", "Other")
            recyclability = product.get("recyclability", "Medium")
            origin = origin_country

            # === Normalize and encode
            material = normalize_feature(material, "Other")
            recyclability = normalize_feature(recyclability, "Medium")
            origin = normalize_feature(origin, "Other")
            transport = transport_mode

            material_encoded = safe_encode(material, material_encoder, "Other")
            transport_encoded = safe_encode(transport, transport_encoder, "Land")
            recycle_encoded = safe_encode(recyclability, recycle_encoder, "Medium")
            origin_encoded = safe_encode(origin, origin_encoder, "Other")

            # === Prepare input
            weight_log = np.log1p(weight)
            weight_bin_encoded = 2 if weight > 0.5 else 1 if weight > 0.1 else 0

            X = [[
                material_encoded,
                transport_encoded,
                recycle_encoded,
                origin_encoded,
                weight_log,
                weight_bin_encoded
            ]]

            prediction = model.predict(X)[0]
            eco_score_ml = label_encoder.inverse_transform([prediction])[0]

            confidence = 0.0
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)
                confidence = round(float(np.max(proba[0])) * 100, 1)

            print(f"✅ ML Score: {eco_score_ml} ({confidence}%)")

        except Exception as e:
            print(f"⚠️ ML prediction failed: {e}")
            eco_score_ml = "N/A"
            confidence = None


        # Assemble response
        return jsonify({
            "data": {
                "attributes": {
                    "origin": origin_country,
                    "weight_kg": round(weight, 2),
                    "raw_product_weight_kg": round(raw_weight, 2),
                    "transport_mode": transport_mode,
                    "default_transport_mode": default_mode,
                    "selected_transport_mode": override_mode or None,
                    "carbon_kg": carbon_kg,
                    "eco_score_ml": eco_score_ml,
                    "eco_score_confidence": confidence,
                    "eco_score_rule_based": eco_score_rule,
           

                    "distance_from_origin_km": origin_distance_km,
                    "distance_from_uk_hub_km": uk_distance_km,
                },
                "title": product.get("title")
            }
        })

    except Exception as e:
        print(f"❌ Uncaught error in estimate_emissions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/test_post", methods=["POST"])
def test_post():
    try:
        data = request.get_json()
        print("✅ Received test POST:", data)
        return jsonify({"message": "Success", "you_sent": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "✅ Server is up"}), 200



@app.route("/")
def home():
    return "<h2>🌍 Flask is running</h2>"

@app.route("/test")
def test():
    return "✅ Flask test OK"



#if __name__ == "__main__":
 #   print("🚀 Flask is launching...")
  #  app.run(debug=True)
   # host="0.0.0.0", port=5000,
   
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
 