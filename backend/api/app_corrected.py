
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import json
import pandas as pd
import numpy as np
from backend.scrapers.amazon.scrape_amazon_titles import scrape_amazon_product_page, estimate_origin_country

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
model_dir = os.path.join(BASE_DIR, "backend", "ml", "models")
encoders_dir = os.path.join(BASE_DIR, "backend", "ml", "encoders")

app = Flask(__name__)
app.secret_key = "super-secret-key"
CORS(app, supports_credentials=True)

model = joblib.load(os.path.join(model_dir, "eco_model.pkl"))
material_encoder = joblib.load(os.path.join(encoders_dir, "material_encoder.pkl"))
transport_encoder = joblib.load(os.path.join(encoders_dir, "transport_encoder.pkl"))
recycle_encoder = joblib.load(os.path.join(encoders_dir, "recycle_encoder.pkl"))
label_encoder = joblib.load(os.path.join(encoders_dir, "label_encoder.pkl"))
origin_encoder = joblib.load(os.path.join(encoders_dir, "origin_encoder.pkl"))

with open(os.path.join(model_dir, "feature_order.json")) as f:
    FEATURE_ORDER = json.load(f)

def normalize_feature(value, default):
    clean = str(value or default).strip().title()
    return default if clean.lower() == "unknown" else clean

def safe_encode(value, encoder, default):
    value = normalize_feature(value, default)
    if value not in encoder.classes_:
        value = default
    return encoder.transform([value])[0]

@app.route("/estimate_emissions", methods=["POST"])
def estimate_emissions():
    try:
        data = request.get_json()
        url = data.get("amazon_url")
        product = scrape_amazon_product_page(url) if url else {}

        material = normalize_feature(product.get("material_type", data.get("material")), "Other")
        transport = normalize_feature(data.get("transport"), "Land")
        recyclability = normalize_feature(product.get("recyclability", data.get("recyclability")), "Medium")
        origin = normalize_feature(product.get("brand_estimated_origin", data.get("origin")), "Other")
        raw_weight = float(product.get("raw_product_weight_kg") or data.get("weight") or 0.5)
        weight = raw_weight * 1.05

        weight_log = np.log(weight + 1e-5)
        weight_bin_encoded = 2 if weight > 0.5 else 1 if weight > 0.1 else 0

        feature_dict = {
            "material_encoded": safe_encode(material, material_encoder, "Other"),
            "transport_encoded": safe_encode(transport, transport_encoder, "Land"),
            "recyclability_encoded": safe_encode(recyclability, recycle_encoder, "Medium"),
            "origin_encoded": safe_encode(origin, origin_encoder, "Other"),
            "weight_log": weight_log,
            "weight_bin_encoded": weight_bin_encoded
        }
        X = pd.DataFrame([[feature_dict[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

        prediction = model.predict(X)[0]
        decoded_score = label_encoder.inverse_transform([prediction])[0]
        confidence = round(max(model.predict_proba(X)[0]) * 100, 1)

        return jsonify({
            "data": {
                "attributes": {
                    "eco_score_ml": decoded_score,
                    "eco_score_confidence": confidence,
                    "material_type": material,
                    "weight_kg": round(weight, 2),
                    "transport_mode": transport,
                    "recyclability": recyclability,
                    "origin": origin
                },
                "title": product.get("title", "Unknown")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "up"})

if __name__ == "__main__":
    app.run(debug=True)
