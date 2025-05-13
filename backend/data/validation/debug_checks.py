import pandas as pd
import joblib

# === Check 1: What's in the eco_score column?
df = pd.read_csv("ml_model/eco_dataset.csv")
print("✅ Unique eco scores:", df["true_eco_score"].unique())

# === Check 2: Check material encoder
material_encoder = joblib.load("ml_model/encoders/material_encoder.pkl")
print("✅ Material encoder classes:", material_encoder.classes_)

# === Check 3: Check label encoder
label_encoder = joblib.load("ml_model/encoders/label_encoder.pkl")
print("✅ Label encoder classes:", label_encoder.classes_)
