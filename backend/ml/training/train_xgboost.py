import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from imblearn.over_sampling import SMOTE
from collections import Counter
import json

# === Paths ===
script_dir = os.path.dirname(__file__)
csv_path = os.path.abspath(os.path.join(script_dir, "../../../common/data/csv/eco_dataset.csv"))
model_dir = os.path.join(script_dir, "..", "models")
encoders_dir = os.path.join(script_dir, "..", "encoders")
os.makedirs(model_dir, exist_ok=True)
os.makedirs(encoders_dir, exist_ok=True)

# === Load and preprocess dataset ===
column_names = ["title", "material", "weight", "transport", "recyclability", "true_eco_score", "co2_emissions", "origin"]
df = pd.read_csv(csv_path, header=None, names=column_names, quotechar='"')
df = df[df["true_eco_score"].isin(["A+", "A", "B", "C", "D", "E", "F"])].dropna()

# === Clean up string fields
for col in ["material", "transport", "recyclability", "origin"]:
    df[col] = df[col].astype(str).str.title().str.strip()

# === Weight prep
df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
df.dropna(subset=["weight"], inplace=True)
df["weight_log"] = np.log1p(df["weight"])
df["weight_bin"] = pd.cut(df["weight"], bins=[0, 0.5, 2, 10, 100], labels=[0, 1, 2, 3])

# === Label encoding
encoders = {
    'material': LabelEncoder(),
    'transport': LabelEncoder(),
    'recyclability': LabelEncoder(),
    'origin': LabelEncoder(),
    'label': LabelEncoder(),
    'weight_bin': LabelEncoder()
}

for key in encoders:
    col = key if key != "label" else "true_eco_score"
    df[f"{key}_encoded"] = encoders[key].fit_transform(df[col].astype(str))

# === Feature selection
feature_cols = [
    "material_encoded",
    "transport_encoded",
    "recyclability_encoded",
    "origin_encoded",
    "weight_log",
    "weight_bin_encoded"
]
X = df[feature_cols].astype(float)
y = df["label_encoded"]

# === Save feature order
with open(os.path.join(model_dir, "feature_order.json"), "w") as f:
    json.dump(feature_cols, f)

# === Balance the data
X_balanced, y_balanced = SMOTE(random_state=42).fit_resample(X, y)

# === Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced, test_size=0.2, stratify=y_balanced, random_state=42
)

# === Class weights
counter = Counter(y_balanced)
total = sum(counter.values())
class_weights = {cls: total / count for cls, count in counter.items()}
sample_weights = [class_weights[i] for i in y_train]

# === XGBoost Model + Hyperparameter Search
base_model = xgb.XGBClassifier(
    use_label_encoder=False,
    eval_metric="mlogloss",
    n_estimators=300,
    max_depth=7,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    random_state=42
)

params = {
    "n_estimators": [200, 300],
    "max_depth": [6, 7],
    "learning_rate": [0.05, 0.08],
    "subsample": [0.7, 0.85],
    "colsample_bytree": [0.7, 0.85]
}

search = RandomizedSearchCV(base_model, params, scoring="f1_macro", n_iter=5, cv=3)
search.fit(X_train, y_train, sample_weight=sample_weights)
model = search.best_estimator_

# === Evaluate
y_pred = model.predict(X_test)
acc = model.score(X_test, y_test)
f1 = f1_score(y_test, y_pred, average="macro")
report = classification_report(y_test, y_pred, target_names=encoders['label'].classes_, output_dict=True)

print(f"✅ Accuracy: {acc:.4f}")
print(f"✅ F1 Score: {f1:.4f}")

# === Save model + encoders
joblib.dump(model, os.path.join(model_dir, "eco_model.pkl"))
for name, enc in encoders.items():
    joblib.dump(enc, os.path.join(encoders_dir, f"{name}_encoder.pkl"))

# === Save metrics
with open(os.path.join(model_dir, "xgb_metrics.json"), "w") as f:
    json.dump({
        "accuracy": round(acc, 4),
        "f1_score": round(f1, 4),
        "report": report
    }, f, indent=2)

print("✅ Model, encoders, and metrics saved successfully.")
