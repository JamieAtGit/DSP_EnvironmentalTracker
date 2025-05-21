import pandas as pd
import os
import csv

def load_material_co2_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # points to project root
    csv_path = os.path.join(base_dir, "common", "data", "csv", "defra_material_intensity.csv")

    material_co2_map = {}
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mat = row["material"].strip().lower()
                material_co2_map[mat] = float(row["co2_per_kg"])
    except FileNotFoundError:
        print(f"⚠️ CO2 data file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading CO2 data: {e}")

    return material_co2_map
