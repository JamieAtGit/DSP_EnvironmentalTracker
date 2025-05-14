from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import joblib
import sys
import os
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

model_dir = os.path.join(BASE_DIR, "backend", "ml", "models")
encoders_dir = os.path.join(BASE_DIR, "backend", "ml", "encoders")

import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes.auth import register_routes
from api.routes.api import calculate_eco_score


import pandas as pd
from backend.scrapers.amazon.scrape_amazon_titles import (
    scrape_amazon_product_page,
    estimate_origin_country,
    resolve_brand_origin,
    save_brand_locations
)

import csv
import re
import numpy as np

# === Load Flask ===
app = Flask(__name__)
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

        transport = normalize_feature(user_transport or guess_transport_by_distance(origin_km), "Land")
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

        confidence = 0.0
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)
            print("🧪 predict_proba output:", proba)

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
material_encoder = joblib.load(os.path.join(encoders_dir, "material_encoder.pkl"))
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


@app.route("/estimate_emissions", methods=["POST", "OPTIONS"])
def estimate_emissions():
    print("🔔 Route hit: /estimate_emissions")
    if request.method == "OPTIONS":
        return '', 201

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON in request"}), 400

    try:
        url = data.get("amazon_url")
        include_packaging = data.get("include_packaging", True)
        product = {}

        # Attempt to scrape product if URL provided
        if url:
            print(f"🌍 Scraping Amazon product from: {url}")
            product = scrape_amazon_product_page(url)
            print("📦 Scraped product data:", json.dumps(product, indent=2))
        else:
            print("⚠️ No URL provided, using manual data input")

        # Unified extraction of product fields (from scrape or manual)
        title = product.get("title", data.get("title", "Unknown Product"))
        material_raw = product.get("material_type") or data.get("material")
        material = normalize_feature(material_raw, "Other")

        # Fallback: if material is "Other" or absurdly long, extract from title
        if material.lower() == "other" or len(material) > 30:
            guessed = fuzzy_match_material(title)
            if guessed.lower() != "other":
                material = guessed



        transport = normalize_feature(data.get("transport"), "Land")
        recyclability = normalize_feature(product.get("recyclability", data.get("recyclability")), "Medium")
        origin = normalize_feature(product.get("brand_estimated_origin", data.get("origin")), "Other")
        dimensions = product.get("dimensions_cm")
        raw_weight = product.get("raw_product_weight_kg")
        estimated_weight = product.get("estimated_weight_kg")
        origin_distance_km = float(product.get("distance_origin_to_uk") or 0)
        uk_distance_km = float(product.get("distance_uk_to_user") or 0)

        # Fallback for missing weight
        raw_weight = raw_weight or data.get("weight")

        # Estimate missing origin from title if still unknown
        if origin in ["Unknown", "Other", None, ""] and title:
            guessed = estimate_origin_country(title)
            if guessed and guessed.lower() != "other":
                print(f"🧠 Estimated origin from title: {guessed}")
                origin = guessed

        # Final weight calculation
        try:
            weight = float(raw_weight or estimated_weight or 0.5)
        except:
            weight = 0.5
        if include_packaging:
            weight *= 1.05
        print(f"✅ Final product weight: {weight:.2f} kg")

        # Normalization + CO2 estimate
        material = fuzzy_match_material(material)
        if material == "Other" and title:
            guessed = fuzzy_match_material(title)
            if guessed != "Other":
                material = guessed

        origin = fuzzy_match_origin(origin)
        carbon_kg = round(weight * material_co2_map.get(material, 2.0), 2)

        # Build feature vector
        # Additional features
        weight_log = np.log(weight + 1e-5)
        weight_bin_encoded = 2 if weight > 0.5 else 1 if weight > 0.1 else 0

        X = pd.DataFrame([[   
        safe_encode(material, material_encoder, "Other"),
        safe_encode(transport, transport_encoder, "Land"),
        safe_encode(recyclability, recycle_encoder, "Medium"),
        safe_encode(origin, origin_encoder, "Other"),
        weight_log,
        weight_bin_encoded
    ]], columns=[
        "material_encoded",
        "transport_encoded",
        "recycle_encoded",
        "origin_encoded",
        "weight_log",
        "weight_bin_encoded"
    ])


        print("🧪 Final input to model:", X.values.tolist())
        proba = model.predict_proba(X)
        print("🧪 Model predict_proba output:", proba)

        # Predict score
        decoded_score = "C"
        confidence = 0.0
        try:
            prediction = model.predict(X)[0]
            decoded_score = label_encoder.inverse_transform([prediction])[0]
            if decoded_score not in valid_scores:
                decoded_score = "C"
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)
                print("🔍 predict_proba output:", proba)

                print("🔍 Model predict_proba output:", proba[0])

                if proba is not None and len(proba[0]) > 0:
                    confidence = round(max(proba[0]) * 100, 1)
        except Exception as e:
            print(f"⚠️ Prediction failed: {e}")

        # Log full dataset
        try:
            with open(os.path.join(model_dir, "eco_dataset.csv"), "a", newline='', encoding="utf-8") as f:
                csv.writer(f, quoting=csv.QUOTE_MINIMAL).writerow([
                    title, material, f"{weight:.2f}", transport, recyclability, decoded_score, carbon_kg, origin
                ])
        except Exception as e:
            print(f"⚠️ General logging failed: {e}")

        # Conditionally log to real scraped dataset
        try:
            if url and all([
                decoded_score in valid_scores,
                material in material_encoder.classes_,
                transport in transport_encoder.classes_,
                recyclability in recycle_encoder.classes_,
                origin in origin_encoder.classes_
            ]):
                with open(os.path.join(model_dir, "real_scraped_dataset.csv"), "a", newline='', encoding="utf-8") as f:
                    csv.writer(f, quoting=csv.QUOTE_MINIMAL).writerow([
                        title, material, f"{weight:.2f}", transport, recyclability, decoded_score, carbon_kg, origin
                    ])
                print("✅ Logged to real_scraped_dataset.csv")
        except Exception as e:
            print(f"⚠️ Clean logging failed: {e}")

        # Final API response
        emoji_map = {
            "A+": "🌍", "A": "🌿", "B": "🍃",
            "C": "🌱", "D": "⚠️", "E": "❌", "F": "💀"
        }
        
        print("✅ Returning ML confidence:", confidence)
        eco_score_rule = calculate_eco_score(
            carbon_kg,
            recyclability,
            origin_distance_km,
            weight
        )
        print("✅ Returning rule-based score:", eco_score_rule)

        return jsonify({
            "data": {
                "attributes": {
                    "eco_score_ml": decoded_score,
                    "eco_score_confidence": round(confidence, 2),  
                    "eco_score_rule_based": eco_score_rule, 
                    
                    "ml_carbon_kg": round(weight * 1.2, 2),
                    "trees_to_offset": max(1, round(carbon_kg / 15)),
                    "material_type": material,
                    "weight_kg": round(weight, 2),
                    "raw_product_weight_kg": round(float(raw_weight or estimated_weight or 0.5), 2),
                    "transport_mode": transport,
                    "recyclability": recyclability,
                    "origin": origin,
                    "dimensions_cm": dimensions,
                    "carbon_kg": round(carbon_kg, 2),
                    "distance_from_origin_km": origin_distance_km,
                    "distance_from_uk_hub_km": uk_distance_km,
                    "intl_distance_km": origin_distance_km,
                    "uk_distance_km": uk_distance_km
                },
                "title": title
            }
        })
        


    except Exception as e:
        print(f"❌ Uncaught error: {e}")
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
 