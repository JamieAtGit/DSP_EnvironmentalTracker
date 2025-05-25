#BOOTSTRAP
import sys
print(sys.executable)
import csv
import os
import json
import random
import re
import time
from datetime import datetime
import difflib

# Debug: print interpreter path
print("🧠 Python running from:", sys.executable)

# Step 1: Point to your project root (DEV/DSP)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Step 2: Now you can import from common
from common.data.brand_origin_resolver import get_brand_origin, get_brand_origin_intelligent
from backend.utils.co2_data import load_material_co2_data

import traceback
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from backend.utils.co2_data import load_material_co2_data
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


CHROMEDRIVER_PATH = r"C:\Dev\DSP\tools\selenium\chromedriver\chromedriver.exe"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("window-size=1280,800")

#driver_path = ChromeDriverManager(version="136.0.7103.114").install()
#print("🚀 Using ChromeDriver from:", driver_path)


material_co2_map = load_material_co2_data()

fallback_mode = False

ua = UserAgent()
random_user_agent = ua.random
chrome_options.add_argument(f"user-agent={random_user_agent}")
print(f"🧢 Using User-Agent: {random_user_agent}")

# === ChromeDriver instantiation should happen *inside* your scraping functions
# For test or fallback mode only:
fallback_mode = False
print("⚠️ Fallback mode:", fallback_mode)

# === CO2 Lookup Table
material_co2_map = load_material_co2_data()

#service = Service(ChromeDriverManager().install())
#driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

#driver = webdriver.Chrome(service=service, options=chrome_options)
print("⚠️ Running fallback mode — scraper disabled on remote deployment.")
fallback_mode = False

# Quick test
#driver.get("https://www.google.com")
#print(driver.title)
#driver.quit()

# === Load custom brand location metadata ===

class Log:
    @staticmethod
    def info(msg): print(f"\033[94mℹ️ {msg}\033[0m")
    @staticmethod
    def success(msg): print(f"\033[92m✅ {msg}\033[0m")
    @staticmethod
    def warn(msg): print(f"\033[93m⚠️ {msg}\033[0m")
    @staticmethod
    def error(msg): print(f"\033[91m❌ {msg}\033[0m")

def safe_get(driver, url, retries=3, wait=10):
    for i in range(retries):
        try:
            driver.get(url)
            time.sleep(wait)

            # Check for anti-bot blocks
            page_source = driver.page_source.lower()
            if any(block in page_source for block in ["robot check", "service unavailable", "we're sorry"]):
                Log.warn(f"🚫 Blocked or 503 at {url}. Retrying ({i+1}/{retries})...")
                continue  # Try again

            return True
        except Exception as e:
            Log.warn(f"❌ Failed to load {url} (attempt {i+1}): {e}")
            time.sleep(wait * (i+1))
    return False




# === PRIORITY PRODUCTS DB ===
priority_products = {}
try:
    with open("priority_products.json", "r", encoding="utf-8") as f:
        priority_products = json.load(f)
    Log.success(f"✅ Loaded {len(priority_products)} high-accuracy products.")
except FileNotFoundError:
    Log.warn("priority_products.json not found. Starting with empty product DB.")
except Exception as e:
    Log.error(f"Error loading priority product DB: {e}")


brand_locations = {}
try:
    with open("brand_locations.json", "r", encoding="utf-8") as f:
        brand_locations = json.load(f)
    Log.success(f"📦 Loaded {len(brand_locations)} custom brand locations.")
except Exception as e:
    Log.warn(f" Could not load brand_locations.json: {e}")


# === CONFIG ===
ua = UserAgent()
chrome_options = Options()
chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("window-size=1280,800")  # 🖥️ Simulate realistic screen
chrome_options.add_argument("--lang=en-GB")  # Optional: browser language


# 🧢 Rotate user-agent for stealth
random_user_agent = ua.random
chrome_options.add_argument(f"user-agent={random_user_agent}")
Log.info(f"🧢 Using User-Agent: {random_user_agent}")



# === Load external brand origins CSV ===
brand_origin_lookup = {}
try:
    with open("brand_origins.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand = row["brand"].lower()
            brand_origin_lookup[brand] = {
                "country": row["hq_country"],
                "city": row["hq_city"]
            }
except FileNotFoundError:
    Log.warn("brand_origins.csv not found. Defaulting to heuristic mapping.")


origin_hubs = {
    "China": {"lat": 31.2304, "lon": 121.4737, "city": "Shanghai"},
    "Germany": {"lat": 50.1109, "lon": 8.6821, "city": "Frankfurt"},
    "USA": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco"},
    "Japan": {"lat": 35.6895, "lon": 139.6917, "city": "Tokyo"},
    "UK": {"lat": 51.509865, "lon": -0.118092, "city": "London"},
    "Italy": {"city": "Castel San Giovanni", "lat": 45.0667, "lon": 9.4167},
    "India": {"lat": 28.6139, "lon": 77.2090, "city": "New Delhi"},
    "South Korea": {"lat": 37.5665, "lon": 126.9780, "city": "Seoul"},
    "Spain": {"lat": 40.4168, "lon": -3.7038, "city": "Madrid"},
    "Poland": {"lat": 52.2297, "lon": 21.0122, "city": "Warsaw"},
    "Netherlands": {"lat": 52.3676, "lon": 4.9041, "city": "Amsterdam"},
    "Indonesia": {"lat": -6.2088, "lon": 106.8456, "city": "Jakarta"},
    "France": {"lat": 48.8566, "lon": 2.3522, "city": "Paris"},
    "Ireland": {"lat": 53.3498, "lon": -6.2603, "city": "Dublin"},
    "Canada": {"lat": 45.4215, "lon": -75.6972, "city": "Ottawa"},
    "Switzerland": {"lat": 46.9480, "lon": 7.4474, "city": "Bern"},
    "Australia": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney"},
    "Sweden": {"lat": 59.3293, "lon": 18.0686, "city": "Stockholm"},
    "Finland": {"lat": 60.1699, "lon": 24.9384, "city": "Helsinki"},
    "Mexico": {"lat": 19.4326, "lon": -99.1332, "city": "Mexico City"},
    "Belgium": {"lat": 50.8503, "lon": 4.3517, "city": "Brussels"},
    "Denmark": {"lat": 55.6761, "lon": 12.5683, "city": "Copenhagen"},
    "Norway": {"lat": 59.9139, "lon": 10.7522, "city": "Oslo"},
    "Thailand": {"lat": 13.7563, "lon": 100.5018, "city": "Bangkok"},
    "Vietnam": {"lat": 21.0285, "lon": 105.8542, "city": "Hanoi"},
    "Turkey": {"lat": 39.9334, "lon": 32.8597, "city": "Ankara"},
    "Brazil": {"lat": -23.5505, "lon": -46.6333, "city": "Sao Paulo"},
}
uk_hub = {"lat": 51.8821, "lon": -0.5057, "city": "Dunstable"}

known_brand_origins = {
    "huel": "UK",
    "the bulk protein company": "UK",
    "bulk protein company": "UK",
    "mitre": "UK",
    "avm": "Germany",
    "anker": "China",
    "bosch": "Germany",
    "philips": "Netherlands",
    "sony": "Japan",
    "samsung": "South Korea",
    "apple": "USA",
    "lenovo": "China",
    "asus": "Taiwan",
    "fender": "USA",
    "kinetica": "Ireland",
    "xiaomi": "China",
    "dyson": "UK",
    "adidas": "Germany",
    "nokia": "Finland",
    "logitech": "Switzerland",
    "tcl": "China",
    "tefal": "France",
    "panasonic": "Japan",
    "microsoft": "USA",
    "nintendo": "Japan",
    "uno": {"country": "USA", "source": "brand_db"},
    "mattel": {"country": "USA", "source": "brand_db"},

}


amazon_fulfillment_centers = {
    "UK": {"lat": 51.8821, "lon": -0.5057, "city": "Dunstable"},
    "Germany": {"lat": 50.1109, "lon": 8.6821, "city": "Frankfurt"},
    "France": {"lat": 48.8566, "lon": 2.3522, "city": "Paris"},
    "Italy": {"lat": 45.0667, "lon": 9.4167, "city": "Castel San Giovanni"},
    "USA": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco"},
    "Spain": {"lat": 40.4168, "lon": -3.7038, "city": "Madrid"},
    "Netherlands": {"lat": 52.3676, "lon": 4.9041, "city": "Amsterdam"},
    "Poland": {"lat": 52.2297, "lon": 21.0122, "city": "Warsaw"},
}


def fuzzy_normalize_origin(raw_origin):
    if not raw_origin:
        return "Unknown"

    origin = raw_origin.strip().lower()

    # Keyword-based fuzzy mapping
    fuzzy_map = {
        "UK": ["united kingdom", "uk", "england", "scotland", "wales", "britain", "great britain"],
        "USA": ["united states", "united states of america", "us", "usa", "america"],
        "China": ["china", "prc", "people's republic of china"],
        "Germany": ["germany", "deutschland"],
        "France": ["france"],
        "Italy": ["italy", "italia"],
        "Japan": ["japan", "nippon"],
        "Ireland": ["ireland", "eire"],
        "Netherlands": ["netherlands", "holland"],
        "Canada": ["canada"],
        "Switzerland": ["switzerland"],
        "Australia": ["australia"],
        "Sweden": ["sweden"],
        "Finland": ["finland"],
        "Mexico": ["mexico"],
        "Indonesia": ["indonesia"],
        "India": ["india"],
        "Spain": ["spain", "espana"],
        "Poland": ["poland", "polska"],
        "Belgium": ["belgium"],
        "Denmark": ["denmark"],
        "Norway": ["norway"],
        "South Korea": ["south korea", "korea", "republic of korea"],
        "Thailand": ["thailand"],
        "Vietnam": ["vietnam"],
        "Turkey": ["turkey"],
        "Brazil": ["brazil"],
    }

    for country, keywords in fuzzy_map.items():
        if any(keyword in origin for keyword in keywords):
            return country.title()

    return raw_origin.title()


def estimate_origin_country(title):
    title = title.lower()
    if "huawei" in title:
        return "China"
    elif "adidas" in title:
        return "Germany"
    elif "apple" in title:
        return "USA"
    elif "nike" in title:
        return "USA"  # Nike HQ is in USA, but products are made globally
    elif "sony" in title:
        return "Japan"
    elif "dyson" in title:
        return "UK"
    return "China"

def extract_origin_from_structured_data(driver):
    """
    Extract origin from Amazon's structured data sections
    Returns: {"found": bool, "country": str, "method": str, "raw_text": str}
    """
    try:
        # Method 1: Product Details table (highest priority)
        details_selectors = [
            "table.a-keyvalue tr",
            "#detailBullets_feature_div li",
            ".a-section table tr"
        ]
        
        for selector in details_selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                for row in rows:
                    row_text = row.text.lower()
                    if "country of origin" in row_text:
                        # Extract the value after "country of origin"
                        match = re.search(r"country\s+of\s+origin[:\s]*([a-zA-Z\s,]+)", row_text, re.IGNORECASE)
                        if match:
                            raw_country = match.group(1).strip()
                            normalized_country = fuzzy_normalize_origin(raw_country)
                            if normalized_country != "Unknown":
                                return {
                                    "found": True,
                                    "country": normalized_country,
                                    "method": f"product_details_table_{selector}",
                                    "raw_text": row.text.strip()
                                }
            except Exception as e:
                continue
        
        # Method 2: Technical Specifications section
        try:
            tech_specs = driver.find_elements(By.CSS_SELECTOR, "#technicalSpecifications_section_1 tr")
            for spec_row in tech_specs:
                spec_text = spec_row.text.lower()
                if "country" in spec_text and "origin" in spec_text:
                    cells = spec_row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        country_value = cells[1].text.strip()
                        normalized_country = fuzzy_normalize_origin(country_value)
                        if normalized_country != "Unknown":
                            return {
                                "found": True,
                                "country": normalized_country,
                                "method": "technical_specifications",
                                "raw_text": spec_row.text.strip()
                            }
        except Exception as e:
            pass
        
        # Method 3: Product feature bullets with explicit origin mention
        try:
            bullets = driver.find_elements(By.CSS_SELECTOR, "#feature-bullets li, .a-unordered-list li")
            for bullet in bullets:
                bullet_text = bullet.text.lower()
                if "country of origin" in bullet_text or "made in" in bullet_text:
                    # Extract country from bullet point
                    origin_patterns = [
                        r"country\s+of\s+origin[:\s]*([a-zA-Z\s,]+)",
                        r"made\s+in[:\s]*([a-zA-Z\s,]+)"
                    ]
                    for pattern in origin_patterns:
                        match = re.search(pattern, bullet_text, re.IGNORECASE)
                        if match:
                            raw_country = match.group(1).strip()
                            # Clean up trailing text
                            raw_country = re.sub(r'[,;.].*$', '', raw_country).strip()
                            normalized_country = fuzzy_normalize_origin(raw_country)
                            if normalized_country != "Unknown":
                                return {
                                    "found": True,
                                    "country": normalized_country,
                                    "method": "feature_bullets",
                                    "raw_text": bullet.text.strip()
                                }
        except Exception as e:
            pass
            
        # No structured origin data found
        return {"found": False, "country": "Unknown", "method": "none", "raw_text": ""}
        
    except Exception as e:
        print(f"⚠️ Error in structured origin extraction: {e}")
        return {"found": False, "country": "Unknown", "method": "error", "raw_text": str(e)}

def extract_weight_from_structured_data(driver):
    """
    Extract weight from Amazon's structured data sections  
    Returns: {"found": bool, "weight_kg": float, "method": str, "raw_text": str}
    """
    try:
        # Method 1: Product Dimensions with weight (highest priority)
        page_text = driver.page_source
        
        # Enhanced patterns for dimensions + weight
        dimension_patterns = [
            r"product\s+dimensions[:\s]+[\d\s.x×*cm;,]+[;,]\s*([\d.]+)\s*g\b",
            r"package\s+dimensions[:\s]+[\d\s.x×*cm;,]+[;,]\s*([\d.]+)\s*g\b",
            r"[\d.]+\s*[x×]\s*[\d.]+\s*[x×]\s*[\d.]+\s*cm[;,\s]+([\d.]+)\s*g\b"
        ]
        
        for pattern in dimension_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                weight_grams = float(match.group(1))
                weight_kg = weight_grams / 1000
                return {
                    "found": True,
                    "weight_kg": weight_kg,
                    "method": "product_dimensions",
                    "raw_text": match.group(0)
                }
        
        # Method 2: Dedicated weight fields in product details
        details_selectors = [
            "table.a-keyvalue tr",
            "#detailBullets_feature_div li"
        ]
        
        for selector in details_selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                for row in rows:
                    row_text = row.text.lower()
                    if any(kw in row_text for kw in ["weight", "item weight", "shipping weight"]):
                        # Extract weight value
                        weight_patterns = [
                            r"([\d.]+)\s*kg\b",
                            r"([\d.]+)\s*g\b"
                        ]
                        for w_pattern in weight_patterns:
                            w_match = re.search(w_pattern, row_text)
                            if w_match:
                                weight_val = float(w_match.group(1))
                                if "kg" in w_match.group(0):
                                    weight_kg = weight_val
                                else:  # grams
                                    weight_kg = weight_val / 1000
                                
                                return {
                                    "found": True,
                                    "weight_kg": weight_kg,
                                    "method": f"product_details_{selector}",
                                    "raw_text": row.text.strip()
                                }
            except Exception as e:
                continue
        
        # No structured weight data found
        return {"found": False, "weight_kg": 0, "method": "none", "raw_text": ""}
        
    except Exception as e:
        print(f"⚠️ Error in structured weight extraction: {e}")
        return {"found": False, "weight_kg": 0, "method": "error", "raw_text": str(e)}

def extract_materials_from_structured_data(driver):
    """
    Extract ALL materials from Amazon's structured data sections
    Returns: {"found": bool, "materials": [{"name": str, "confidence": str, "weight": float}], "primary_material": str, "method": str, "raw_text": str}
    """
    try:
        all_materials = []
        
        details_selectors = [
            "table.a-keyvalue tr",
            "#detailBullets_feature_div li"
        ]
        
        for selector in details_selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                for row in rows:
                    row_text = row.text.lower()
                    original_text = row.text.strip()
                    
                    # Look for material field patterns
                    material_patterns = [
                        (r"material[:\s]*([a-zA-Z\s,]+)", "high"),
                        (r"(?:sole|outer|upper|lining)\s+material[:\s]*([a-zA-Z\s,]+)", "high"),
                        (r"(?:material|fabric)\s+(?:composition|type)[:\s]*([a-zA-Z\s,]+)", "medium"),
                        (r"made\s+(?:of|from)[:\s]*([a-zA-Z\s,]+)", "medium")
                    ]
                    
                    # Debug: Log what we're checking
                    if "material" in row_text:
                        print(f"🔍 DEBUG: Found 'material' in row: {original_text[:100]}...")
                    
                    for pattern, confidence in material_patterns:
                        match = re.search(pattern, row_text, re.IGNORECASE)
                        if match:
                            raw_materials = match.group(1).strip()
                            
                            # Parse multiple materials: "Aluminium, Plastic" -> ["Aluminium", "Plastic"]
                            materials_found = parse_multiple_materials(raw_materials)
                            
                            for material_info in materials_found:
                                if material_info["normalized"] != "Unknown":
                                    all_materials.append({
                                        "name": material_info["normalized"],
                                        "confidence": confidence,
                                        "weight": material_info["weight"],
                                        "method": f"structured_{selector}",
                                        "raw_text": original_text
                                    })
                            
                            if materials_found:  # Found materials in this row, don't check other patterns
                                break
                                
            except Exception as e:
                continue
        
        if all_materials:
            # Remove duplicates and prioritize by confidence and material importance
            unique_materials = deduplicate_and_prioritize_materials(all_materials)
            primary_material = determine_primary_material(unique_materials)
            
            return {
                "found": True,
                "materials": unique_materials,
                "primary_material": primary_material,
                "method": "structured_multi_material",
                "raw_text": "; ".join([m["raw_text"] for m in unique_materials[:3]])  # First 3 sources
            }
        
        # No structured material data found
        return {"found": False, "materials": [], "primary_material": "Unknown", "method": "none", "raw_text": ""}
        
    except Exception as e:
        print(f"⚠️ Error in structured material extraction: {e}")
        return {"found": False, "materials": [], "primary_material": "Unknown", "method": "error", "raw_text": str(e)}

def parse_multiple_materials(raw_materials_text):
    """
    Parse text like "Aluminium, Plastic" or "59% Rubber, 41% Cotton" into structured materials
    Returns: [{"raw": str, "normalized": str, "weight": float}, ...]
    """
    materials = []
    
    # Handle percentage-based materials: "59% Rubber, 41% Cotton"
    percentage_pattern = r"(\d+)%\s*([a-zA-Z\s\-]+)"
    percentage_matches = re.findall(percentage_pattern, raw_materials_text, re.IGNORECASE)
    
    if percentage_matches:
        for percent_str, material_name in percentage_matches:
            weight = float(percent_str) / 100.0
            normalized = normalize_material(material_name.strip())
            materials.append({
                "raw": f"{percent_str}% {material_name.strip()}",
                "normalized": normalized,
                "weight": weight
            })
    else:
        # Handle comma-separated materials: "Aluminium, Plastic"
        material_parts = [part.strip() for part in raw_materials_text.split(',')]
        
        # If multiple materials, assume equal weight distribution
        weight_per_material = 1.0 / len(material_parts) if len(material_parts) > 1 else 1.0
        
        for material_part in material_parts:
            # Clean up the material name
            cleaned_material = re.sub(r'[^\w\s-]', '', material_part).strip()
            if len(cleaned_material) > 1:  # Avoid single characters
                normalized = normalize_material(cleaned_material)
                if normalized != "Unknown":
                    materials.append({
                        "raw": material_part,
                        "normalized": normalized,
                        "weight": weight_per_material
                    })
    
    return materials

def deduplicate_and_prioritize_materials(materials_list):
    """Remove duplicates and prioritize materials by importance and confidence"""
    
    # Material priority ranking (higher number = more important for environmental impact)
    material_priority = {
        "Aluminum": 9, "Aluminium": 9, "Steel": 8, "Metal": 7,
        "Glass": 6, "Leather": 5, "Cotton": 4, "Rubber": 3,
        "Plastic": 2, "Synthetic": 1, "Unknown": 0
    }
    
    # Confidence priority
    confidence_priority = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    
    # Group by material name to remove duplicates
    material_groups = {}
    for material in materials_list:
        name = material["name"]
        if name not in material_groups:
            material_groups[name] = material
        else:
            # Keep the one with higher confidence
            if confidence_priority.get(material["confidence"], 0) > confidence_priority.get(material_groups[name]["confidence"], 0):
                material_groups[name] = material
    
    # Sort by priority (environmental impact) and confidence
    unique_materials = list(material_groups.values())
    unique_materials.sort(
        key=lambda m: (
            material_priority.get(m["name"], 0),
            confidence_priority.get(m["confidence"], 0)
        ), 
        reverse=True
    )
    
    return unique_materials

def determine_primary_material(materials_list):
    """Determine the primary material for environmental scoring"""
    if not materials_list:
        return "Unknown"
    
    # Primary material is the highest priority material found
    return materials_list[0]["name"]

def calculate_compound_recyclability(materials_list):
    """
    Calculate weighted recyclability for compound materials
    Returns: (level, percentage, description)
    """
    if not materials_list:
        return "Unknown", 0, "No material information available"
    
    # Individual material recyclability rates
    recyclability_map = {
        "Aluminum": 90, "Aluminium": 90, "Steel": 85, "Glass": 80,
        "Paper": 75, "Cardboard": 88, "Cotton": 50, "Polyester": 45,
        "Plastic": 55, "Rubber": 20, "Leather": 10, "Synthetic": 30,
        "Metal": 80, "Unknown": 0
    }
    
    # Calculate weighted average
    total_weight = sum(m["weight"] for m in materials_list)
    if total_weight == 0:
        total_weight = 1.0  # Avoid division by zero
    
    weighted_recyclability = 0
    material_descriptions = []
    
    for material in materials_list:
        material_recyclability = recyclability_map.get(material["name"], 0)
        weight_contribution = material["weight"] / total_weight
        weighted_recyclability += material_recyclability * weight_contribution
        
        if material_recyclability > 0:
            material_descriptions.append(f"{material['name']} ({material_recyclability}%)")
    
    # Determine overall level
    if weighted_recyclability >= 70:
        level = "High"
    elif weighted_recyclability >= 40:
        level = "Medium"
    elif weighted_recyclability >= 10:
        level = "Low"
    else:
        level = "Very Low"
    
    # Create description
    if len(materials_list) == 1:
        description = f"Single material: {material_descriptions[0] if material_descriptions else 'Unknown material'}"
    else:
        description = f"Compound material: {', '.join(material_descriptions[:3])}"  # Limit to 3 materials
        if len(material_descriptions) > 3:
            description += f" and {len(material_descriptions) - 3} more"
    
    return level, int(weighted_recyclability), description

def get_brand_intelligent_origin(brand_name, product_title="", product_category=""):
    """
    Use brand intelligence combined with product context for smarter origin detection
    Returns: {"country": str, "confidence": str, "reasoning": str}
    """
    brand_lower = brand_name.lower().strip()
    title_lower = product_title.lower()
    
    # Multi-location brands with product-specific manufacturing patterns
    brand_intelligence = {
        "ninja": {
            "headquarters": "USA",
            "manufacturing_patterns": {
                "kitchen appliances": {"primary": "China", "secondary": "Vietnam", "confidence": "medium"},
                "cookware": {"primary": "China", "confidence": "medium"},
                "air fryer": {"primary": "China", "confidence": "high"},
                "blender": {"primary": "China", "confidence": "high"},
                "default": {"primary": "China", "confidence": "low"}
            }
        },
        "instant pot": {
            "headquarters": "Canada", 
            "manufacturing_patterns": {
                "pressure cooker": {"primary": "China", "confidence": "high"},
                "air fryer": {"primary": "China", "confidence": "high"},
                "default": {"primary": "China", "confidence": "medium"}
            }
        },
        "tefal": {
            "headquarters": "France",
            "manufacturing_patterns": {
                "cookware": {"primary": "France", "secondary": "China", "confidence": "medium"},
                "small appliances": {"primary": "China", "confidence": "medium"},
                "default": {"primary": "France", "confidence": "low"}
            }
        },
        "kitchenaid": {
            "headquarters": "USA",
            "manufacturing_patterns": {
                "stand mixer": {"primary": "USA", "confidence": "high"},
                "small appliances": {"primary": "China", "confidence": "medium"},
                "default": {"primary": "USA", "confidence": "low"}
            }
        }
    }
    
    if brand_lower in brand_intelligence:
        brand_info = brand_intelligence[brand_lower]
        patterns = brand_info["manufacturing_patterns"]
        
        # Try to match product category/type
        best_match = None
        for product_type, location_info in patterns.items():
            if product_type in title_lower:
                best_match = location_info
                reasoning = f"Brand {brand_name} + product type '{product_type}' → {location_info['primary']}"
                break
        
        if not best_match:
            best_match = patterns.get("default", {"primary": "Unknown", "confidence": "unknown"})
            reasoning = f"Brand {brand_name} default manufacturing location"
        
        return {
            "country": best_match["primary"],
            "confidence": best_match["confidence"],
            "reasoning": reasoning
        }
    
    # Fallback for unknown brands - try simple heuristics
    if any(word in title_lower for word in ["kitchen", "cooking", "appliance"]):
        return {
            "country": "China",  # Most kitchen appliances manufactured in China
            "confidence": "low",
            "reasoning": "Generic kitchen appliance → likely China manufacturing"
        }
    
    return {
        "country": "Unknown",
        "confidence": "unknown", 
        "reasoning": f"No intelligence available for brand: {brand_name}"
    }


def resolve_origin(scraped, fallback, field_name="country", context=None):
    """
    🎯 MODULAR FIELD RESOLUTION - Intelligent conflict resolution with confidence scoring
    
    This function implements enterprise-grade logic for resolving conflicts between
    scraped data and fallback mappings. Can be reused for any field (origin, material, packaging).
    
    Args:
        scraped: dict with {"value": str, "source": str, "confidence": str}
        fallback: dict with {"value": str, "source": str, "confidence": str} 
        field_name: str - name of field being resolved (for logging)
        context: dict - additional context (brand_name, product_title, category, etc.)
        
    Returns: dict with {"value": str, "confidence": str, "source": str, "reasoning": str}
    
    Logic Rules (as requested):
    1. If scraped matches fallback → high confidence
    2. If they don't match → intelligent logic using source trust hierarchy  
    3. If only fallback exists → medium confidence
    4. If neither exists → "Unknown" with low confidence
    """
    
    # Normalize inputs
    scraped_value = scraped.get("value", "Unknown") if scraped else "Unknown"
    scraped_source = scraped.get("source", "none") if scraped else "none"
    fallback_value = fallback.get("value", "Unknown") if fallback else "Unknown"
    fallback_source = fallback.get("source", "none") if fallback else "none"
    
    context = context or {}
    brand_name = context.get("brand_name", "")
    
    # Source trust hierarchy (higher = more trustworthy)
    source_trust_scores = {
        "page_explicit": 95,        # Direct "Made in China" text
        "techspec_origin": 90,      # Technical specifications section  
        "product_details": 85,      # Product details table
        "blob_fallback": 75,        # Pattern matching in descriptions
        "brand_intelligence": 70,   # AI context-aware analysis
        "shipping_panel": 60,       # Inferred from shipping info
        "brand_db_verified": 55,    # Verified brand database
        "brand_db_generic": 40,     # Generic brand mapping
        "title_guess": 30,          # Heuristic pattern matching
        "none": 0
    }
    
    scraped_trust = source_trust_scores.get(scraped_source, 0)
    fallback_trust = source_trust_scores.get(fallback_source, 0)
    
    # 🎯 RULE 1: Perfect Match → High Confidence
    if scraped_value != "Unknown" and fallback_value != "Unknown" and scraped_value == fallback_value:
        return {
            "value": scraped_value,
            "confidence": "very_high",
            "source": f"{scraped_source}_confirmed",
            "reasoning": f"✅ Scraped data ({scraped_source}) matches fallback ({fallback_source}): {scraped_value}"
        }
    
    # 🎯 RULE 2: Conflict Resolution → Trust Hierarchy + Context
    elif scraped_value != "Unknown" and fallback_value != "Unknown" and scraped_value != fallback_value:
        
        # High-trust scraped data wins
        if scraped_trust >= 85:
            return {
                "value": scraped_value,
                "confidence": "high", 
                "source": scraped_source,
                "reasoning": f"📄 High-trust page data ({scraped_source}) overrides fallback: {scraped_value} vs {fallback_value}"
            }
        
        # Medium-trust scraped vs fallback → context matters
        elif scraped_trust >= 60:
            if fallback_trust <= 50:  # Scraped wins over weak fallback
                return {
                    "value": scraped_value,
                    "confidence": "medium_high",
                    "source": scraped_source,
                    "reasoning": f"📝 Medium-trust scraped data ({scraped_source}) preferred over weak fallback: {scraped_value}"
                }
            else:  # Close call → choose higher trust
                winner = scraped_value if scraped_trust >= fallback_trust else fallback_value
                winner_source = scraped_source if scraped_trust >= fallback_trust else fallback_source
                return {
                    "value": winner,
                    "confidence": "medium",
                    "source": f"{winner_source}_contested", 
                    "reasoning": f"⚖️ Close contest: {scraped_value}({scraped_trust}) vs {fallback_value}({fallback_trust}) → chose {winner}"
                }
        
        # Low-trust scraped → fallback wins
        else:
            return {
                "value": fallback_value,
                "confidence": "medium",
                "source": f"{fallback_source}_override",
                "reasoning": f"🔄 Fallback overrides low-trust scraped: {fallback_value} (fallback) vs {scraped_value} (weak scraped)"
            }
    
    # 🎯 RULE 3: Only Scraped Data Available
    elif scraped_value != "Unknown" and fallback_value == "Unknown":
        confidence_map = {
            (95, 100): "high",
            (75, 94): "medium_high", 
            (50, 74): "medium",
            (0, 49): "low_medium"
        }
        
        confidence = "low"
        for (min_score, max_score), conf_level in confidence_map.items():
            if min_score <= scraped_trust <= max_score:
                confidence = conf_level
                break
                
        return {
            "value": scraped_value,
            "confidence": confidence,
            "source": scraped_source,
            "reasoning": f"📋 Only scraped data available from {scraped_source}: {scraped_value} (trust: {scraped_trust})"
        }
    
    # 🎯 RULE 4: Only Fallback Available → Medium Confidence  
    elif scraped_value == "Unknown" and fallback_value != "Unknown":
        return {
            "value": fallback_value,
            "confidence": "medium",
            "source": fallback_source,
            "reasoning": f"🔄 Fallback only: {fallback_value} from {fallback_source} (no scraped data found)"
        }
    
    # 🎯 RULE 5: No Data Available → Unknown with Low Confidence
    else:
        return {
            "value": "Unknown",
            "confidence": "none",
            "source": "no_data",
            "reasoning": f"❌ No reliable {field_name} data found for {brand_name or 'product'}"
        }


def validate_and_merge_origin_sources(scraped_origin, scraped_source, brand_name, product_title=""):
    """
    🔄 ENHANCED ORIGIN RESOLUTION - Now powered by modular resolve_origin() function
    
    This function maintains backward compatibility while leveraging the new modular
    resolve_origin() system with enhanced brand intelligence integration.
    
    Hierarchical Resolution:
    1. Scraped data vs Brand Intelligence (AI-powered contextual analysis)
    2. If no high-confidence match → resolve_origin() with fallback chain
    3. Brand DB fallback as final option
    
    Returns: {"country": str, "confidence": str, "source": str, "reasoning": str}
    """
    
    # Get brand intelligence prediction (AI-powered contextual analysis)
    brand_intel = get_brand_intelligent_origin(brand_name, product_title)
    
    # Get generic brand fallback  
    generic_brand = resolve_brand_origin(brand_name, product_title)
    generic_country = generic_brand[0] if generic_brand else "Unknown"
    
    # Step 1: Check for perfect agreement between scraped data and brand intelligence
    if (scraped_origin != "Unknown" and brand_intel["country"] != "Unknown" and 
        scraped_origin == brand_intel["country"]):
        return {
            "country": scraped_origin,
            "confidence": "very_high", 
            "source": f"{scraped_source}_ai_validated",
            "reasoning": f"✅ Perfect match: Scraped ({scraped_source}) + AI intelligence agree on {scraped_origin}"
        }
    
    # Step 2: Use modular resolve_origin for intelligent conflict resolution
    # Create structured input for the modular function
    scraped_data = {
        "value": scraped_origin,
        "source": scraped_source,
        "confidence": "scraped"
    } if scraped_origin != "Unknown" else None
    
    # Prioritize brand intelligence over generic brand DB
    best_fallback = None
    if brand_intel["country"] != "Unknown" and brand_intel["confidence"] in ["high", "medium"]:
        best_fallback = {
            "value": brand_intel["country"],
            "source": "brand_intelligence", 
            "confidence": brand_intel["confidence"]
        }
    elif generic_country != "Unknown":
        best_fallback = {
            "value": generic_country,
            "source": "brand_db_generic",
            "confidence": "low"
        }
    
    # Apply modular resolution logic
    context = {
        "brand_name": brand_name,
        "product_title": product_title
    }
    
    result = resolve_origin(scraped_data, best_fallback, "country", context)
    
    # Step 3: Enhance reasoning with brand intelligence context when applicable
    if best_fallback and best_fallback["source"] == "brand_intelligence":
        if "brand_intelligence" in result["source"]:
            result["reasoning"] = f"🧠 {brand_intel['reasoning']} (AI analysis)"
        elif result["value"] == brand_intel["country"]:
            result["reasoning"] += f" | AI concurs: {brand_intel['reasoning']}"
        elif brand_intel["country"] != "Unknown":
            result["reasoning"] += f" | AI suggested: {brand_intel['country']} ({brand_intel['reasoning']})"
    
    # Map new modular function output to legacy field names for compatibility
    return {
        "country": result["value"],
        "confidence": result["confidence"], 
        "source": result["source"],
        "reasoning": result["reasoning"]
    }


def apply_validation_to_origin_detection(origin_country, origin_source, brand_key, title):
    """
    Apply the validation logic to improve origin detection quality
    This replaces the previous basic fallback logic
    """
    validation_result = validate_and_merge_origin_sources(
        scraped_origin=origin_country,
        scraped_source=origin_source,
        brand_name=brand_key,
        product_title=title
    )
    
    print(f"🔍 Origin Validation Result: {validation_result['reasoning']}")
    print(f"📊 Final: {validation_result['country']} (confidence: {validation_result['confidence']})")
    
    return (
        validation_result["country"],
        origin_hubs.get(validation_result["country"], {}).get("city", "Unknown"),
        validation_result["source"],
        validation_result["confidence"]
    )


# 🎯 MODULAR FIELD RESOLUTION EXAMPLES - Demonstrating reusability
# These functions show how resolve_origin() can be reused for any product field

def resolve_material(scraped_material_data, brand_name, product_title=""):
    """
    📦 MATERIAL RESOLUTION - Uses modular resolve_origin() for material detection
    
    Example usage of the modular system for material field resolution.
    Demonstrates how the same intelligent logic applies to any product attribute.
    """
    
    # Scraped material data (from Amazon product page)
    scraped = {
        "value": scraped_material_data.get("material", "Unknown"),
        "source": scraped_material_data.get("source", "none"), # e.g. "techspec_material", "title_guess"
        "confidence": scraped_material_data.get("confidence", "medium")
    } if scraped_material_data.get("material") != "Unknown" else None
    
    # Material fallback data (from brand intelligence or category defaults)
    material_fallbacks = {
        "apple": {"value": "Aluminum", "source": "brand_db_verified", "confidence": "high"},
        "nike": {"value": "Synthetic", "source": "brand_db_verified", "confidence": "medium"},
        "ikea": {"value": "Wood", "source": "brand_db_generic", "confidence": "medium"}
    }
    
    fallback = material_fallbacks.get(brand_name.lower())
    
    context = {
        "brand_name": brand_name,
        "product_title": product_title,
        "field_type": "material"
    }
    
    # Use the same modular logic for material resolution
    result = resolve_origin(scraped, fallback, "material", context)
    
    return {
        "material": result["value"],
        "confidence": result["confidence"],
        "source": result["source"], 
        "reasoning": result["reasoning"]
    }


def resolve_packaging(scraped_packaging_data, brand_name, product_title=""):
    """
    📦 PACKAGING RESOLUTION - Uses modular resolve_origin() for packaging type detection
    
    Another example showing how resolve_origin() applies to packaging field resolution
    with the same intelligent conflict resolution and confidence scoring.
    """
    
    # Scraped packaging data (from Amazon product specifications) 
    scraped = {
        "value": scraped_packaging_data.get("packaging_type", "Unknown"),
        "source": scraped_packaging_data.get("source", "none"), # e.g. "product_details", "shipping_panel"
        "confidence": scraped_packaging_data.get("confidence", "medium")
    } if scraped_packaging_data.get("packaging_type") != "Unknown" else None
    
    # Packaging fallback data (from category intelligence)
    packaging_patterns = {
        "electronics": {"value": "Plastic", "source": "category_default", "confidence": "medium"},
        "books": {"value": "Paper", "source": "category_default", "confidence": "high"},
        "food": {"value": "Mixed", "source": "category_default", "confidence": "medium"}
    }
    
    # Determine category from title/brand for fallback
    product_category = "electronics"  # Could be enhanced with AI classification
    if any(word in product_title.lower() for word in ["book", "novel", "guide"]):
        product_category = "books"
    elif any(word in product_title.lower() for word in ["food", "snack", "organic"]):
        product_category = "food"
        
    fallback = packaging_patterns.get(product_category)
    
    context = {
        "brand_name": brand_name,
        "product_title": product_title,
        "product_category": product_category,
        "field_type": "packaging"
    }
    
    # Same modular logic, different field
    result = resolve_origin(scraped, fallback, "packaging_type", context)
    
    return {
        "packaging_type": result["value"],
        "confidence": result["confidence"],
        "source": result["source"],
        "reasoning": result["reasoning"]
    }


def demonstrate_modular_usage():
    """
    🚀 DEMONSTRATION - Shows how the modular resolve_origin() works across different fields
    
    This function provides working examples of how to use the modular system
    for any product attribute with consistent intelligent resolution logic.
    """
    
    # Example product data
    product_data = {
        "brand": "Apple",
        "title": "Apple iPhone 15 Pro Max - 256GB - Natural Titanium",
        "scraped_origin": {"value": "China", "source": "techspec_origin"},
        "scraped_material": {"value": "Titanium", "source": "product_details"},
        "scraped_packaging": {"value": "Cardboard", "source": "shipping_panel"}
    }
    
    print("🎯 MODULAR FIELD RESOLUTION DEMO")
    print("=" * 50)
    
    # 1. Origin Resolution
    origin_result = validate_and_merge_origin_sources(
        scraped_origin=product_data["scraped_origin"]["value"],
        scraped_source=product_data["scraped_origin"]["source"],
        brand_name=product_data["brand"],
        product_title=product_data["title"]
    )
    print(f"🌍 ORIGIN: {origin_result['country']} ({origin_result['confidence']})")
    print(f"   Reasoning: {origin_result['reasoning']}")
    
    # 2. Material Resolution  
    material_result = resolve_material(
        scraped_material_data=product_data["scraped_material"],
        brand_name=product_data["brand"],
        product_title=product_data["title"]
    )
    print(f"\n🔧 MATERIAL: {material_result['material']} ({material_result['confidence']})")
    print(f"   Reasoning: {material_result['reasoning']}")
    
    # 3. Packaging Resolution
    packaging_result = resolve_packaging(
        scraped_packaging_data=product_data["scraped_packaging"],
        brand_name=product_data["brand"],
        product_title=product_data["title"]
    )
    print(f"\n📦 PACKAGING: {packaging_result['packaging_type']} ({packaging_result['confidence']})")
    print(f"   Reasoning: {packaging_result['reasoning']}")
    
    print("\n✅ All fields resolved using the same modular resolve_origin() logic!")
    
    return {
        "origin": origin_result,
        "material": material_result, 
        "packaging": packaging_result
    }

def extract_shipping_origin(driver):
    try:
        candidates = driver.find_elements(By.XPATH, "//div[contains(text(), 'Ships from') or contains(text(), 'Sold by') or contains(text(),'Dispatches from')]")
        for el in candidates:
            text = el.text.lower()
            if "china" in text:
                return "China"
            elif "germany" in text:
                return "Germany"
            elif "united states" in text or "usa" in text:
                return "USA"
            elif "uk" in text or "united kingdom" in text:
                return "UK"
            elif "italy" in text:
                return "Italy"
            elif "france" in text:
                return "France"
    except Exception as e:
        Log.warn(f"⚠️ Could not extract shipping origin: {e}")
    return None


def is_high_confidence(product):
    return (
        product.get("brand_estimated_origin") not in ["Unknown", None] and
        isinstance(product.get("estimated_weight_kg"), (int, float)) and
        product.get("dimensions_cm") not in [None, ""] and
        product.get("asin") is not None
    )

def maybe_add_to_priority(product, priority_db, save_path="priority_products.json"):
    asin = product.get("asin")
    if not asin or asin in priority_db:
        return False

    if is_high_confidence(product):
        product["confidence"] = "High"
        priority_db[asin] = product

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(priority_db, f, indent=2)
        
        Log.success(f"🔐 Added {asin} to priority_products.json")
        return True
    
    return False



def extract_asin(url):
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if not match:
        match = re.search(r"/gp/product/([A-Z0-9]{10})", url)
    if not match:
        match = re.search(r"/product/([A-Z0-9]{10})", url)
    if not match:
        match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
    return match.group(1) if match else None


def extract_weight(text):
    if not text:
        return None

    text = text.lower()

    # 1. Special handling for Product/Package Dimensions format: "45.01 x 30 x 19.99 cm; 0.6 g"
    dims_patterns = [
        r"(?:product|package)\s*dimensions?\s*:?\s*[\d\s.x×*cm;]+;\s*([\d.]+)\s*g",
        r"[\d.]+\s*x\s*[\d.]+\s*x\s*[\d.]+\s*cm;\s*([\d.]+)\s*g",
        r"dimensions?\s*:?\s*[\d\s.x×*cm;]+;\s*([\d.]+)\s*g",
        # More flexible patterns for various Amazon formats
        r"[\d.]+\s*x\s*[\d.]+\s*x\s*[\d.]+\s*cm[;,]\s*([\d.]+)\s*g",
        r"product\s+dimensions\s*[:\s]+[\d\s.x×*cm;,]+[;,]\s*([\d.]+)\s*g",
        # Even more flexible - just look for dimensions followed by weight
        r"[\d.]+\s*[x×]\s*[\d.]+\s*[x×]\s*[\d.]+\s*cm[;,\s]+([\d.]+)\s*g\b"
    ]
    
    for pattern in dims_patterns:
        dims_match = re.search(pattern, text, re.IGNORECASE)
        if dims_match:
            weight_grams = float(dims_match.group(1))
            print(f"⚖️ Found weight in dimensions: {weight_grams}g")
            return round(weight_grams / 1000, 3)

    # 2. Match kg first (also handles "kilogram" or "kilograms")  
    kg_match = re.search(r"([\d.]+)\s?(kg|kilogram|kilograms)", text)
    if kg_match:
        return round(float(kg_match.group(1)), 3)

    # 3. Match grams (more flexible pattern)
    g_match = re.search(r"([\d.]+)\s?(g|grams?|gramme?s?)\b", text)
    if g_match:
        return round(float(g_match.group(1)) / 1000, 3)

    # 4. Weight field with value
    weight_match = re.search(r"(?:weight|item weight)\s*:?\s*([\d.]+)\s*(kg|g|grams?)", text)
    if weight_match:
        weight_val = float(weight_match.group(1))
        unit = weight_match.group(2)
        if unit == "kg":
            return round(weight_val, 3)
        else:  # grams
            return round(weight_val / 1000, 3)

    return None




def extract_dimensions(text):
    match = re.search(r"(\d+(?:\.\d+)?)\s?[x×*]\s?(\d+(?:\.\d+)?)\s?[x×*]\s?(\d+(?:\.\d+)?)(?:\s?cm|centimeters?)", text)
    if match:
        return f"{match.group(1)} x {match.group(2)} x {match.group(3)} cm"
    return None


def normalize_material(raw_material):
    """Normalize and prioritize material names"""
    if not raw_material:
        return "Unknown"
    
    material_lower = raw_material.lower().strip()
    
    # High-priority specific materials
    if "rubber" in material_lower:
        return "Rubber"
    elif "leather" in material_lower:
        return "Leather"
    elif "mesh" in material_lower:
        return "Mesh"
    elif "cotton" in material_lower:
        return "Cotton"
    elif "polyester" in material_lower:
        return "Polyester"
    elif "nylon" in material_lower:
        return "Nylon"
    elif "plastic" in material_lower:
        return "Plastic"
    elif "canvas" in material_lower:
        return "Canvas"
    elif "synthetic" in material_lower:
        return "Synthetic"
    elif "fabric" in material_lower:
        return "Fabric"
    # Medium-priority generic materials  
    elif "compound" in material_lower:
        return "Compound"
    elif "composite" in material_lower:
        return "Composite"
    elif "mixed" in material_lower:
        return "Mixed"
    elif "various" in material_lower:
        return "Mixed"
    elif "textile" in material_lower:
        return "Textile"
    # Return cleaned material name if no specific match
    elif len(material_lower) > 2 and material_lower not in ["other", "unknown", "n/a", "not specified"]:
        return raw_material.title()
    else:
        return "Unknown"

def extract_material(text):
    if not text:
        return None
    
    text = text.lower()
    
    # 1. Priority extraction from specific Amazon material fields (highest priority)
    specific_material_fields = [
        r"sole material\s*:?\s*([a-zA-Z\s\-,]+)",
        r"outer material\s*:?\s*([a-zA-Z\s\-,]+)", 
        r"upper material\s*:?\s*([a-zA-Z\s\-,]+)",
        r"lining material\s*:?\s*([a-zA-Z\s\-,]+)",
        r"main material\s*:?\s*([a-zA-Z\s\-,]+)",
        r"primary material\s*:?\s*([a-zA-Z\s\-,]+)"
    ]
    
    # Check specific materials first (highest priority)
    for field_pattern in specific_material_fields:
        field_match = re.search(field_pattern, text, re.IGNORECASE)
        if field_match:
            raw_material = field_match.group(1).strip()
            # Clean up the material value
            raw_material = re.sub(r'[,;.].*$', '', raw_material).strip()
            raw_material = re.sub(r'\s+(and|or|with|plus).*$', '', raw_material, flags=re.IGNORECASE).strip()
            
            # Prioritize specific materials over generic ones
            material = normalize_material(raw_material)
            if material and material != "Unknown":
                print(f"🧬 Found HIGH PRIORITY material: '{raw_material}' → {material}")
                return material
    
    # 1.5. Check general material composition fields (medium priority)
    general_material_fields = [
        r"material composition\s*:?\s*([a-zA-Z\s\-,]+)",
        r"fabric type\s*:?\s*([a-zA-Z\s\-,]+)",
        r"material\s*:?\s*([a-zA-Z\s\-,]+)"
    ]
    
    composition_material = None
    for field_pattern in general_material_fields:
        field_match = re.search(field_pattern, text, re.IGNORECASE)
        if field_match:
            raw_material = field_match.group(1).strip()
            raw_material = re.sub(r'[,;.].*$', '', raw_material).strip()
            raw_material = re.sub(r'\s+(and|or|with|plus).*$', '', raw_material, flags=re.IGNORECASE).strip()
            
            material = normalize_material(raw_material)
            if material and material != "Unknown":
                composition_material = material
                print(f"🧬 Found MEDIUM PRIORITY material: '{raw_material}' → {material}")
                break

    # 2. Handle detailed material compositions like "59% RUBBER, 16% POLYESTER, 7% TPU, 18% FOAM"
    material_comp_match = re.search(r"material type\s*:?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if material_comp_match:
        comp_text = material_comp_match.group(1).strip()
        # Extract primary material (highest percentage)
        percentage_matches = re.findall(r"(\d+)%\s*([a-z]+)", comp_text, re.IGNORECASE)
        if percentage_matches:
            # Find material with highest percentage
            primary_material = max(percentage_matches, key=lambda x: int(x[0]))
            return primary_material[1].title()
    
    # 3. Extract from construction field
    construction_match = re.search(r"construction\s*:?\s*([a-z\s\-]+)", text, re.IGNORECASE)
    if construction_match:
        material = construction_match.group(1).strip()
        # Extract first material word
        first_material = re.search(r"([a-z]+)", material, re.IGNORECASE)
        if first_material:
            return first_material.group(1).title()
    
    # 4. General material extraction (original logic)
    general_match = re.search(r"(?:material|made of|composition)[\s:]+([a-z\s\-]+)", text, re.IGNORECASE)
    if general_match:
        return general_match.group(1).strip().title()
    
    # 5. Direct material keywords
    material_keywords = ["plastic", "rubber", "leather", "cotton", "polyester", "nylon", 
                        "metal", "steel", "aluminum", "wood", "glass", "ceramic", "silicone"]
    for keyword in material_keywords:
        if keyword in text:
            return keyword.title()
    
    # 6. Return composition material as fallback if found
    if composition_material:
        print(f"🧬 Using FALLBACK composition material: {composition_material}")
        return composition_material
    
    return None




def haversine(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c



def resolve_brand_origin(brand_key, title_fallback=None):
    global brand_locations

    # Normalize brand key
    brand_key = brand_key.lower().strip()
    
    # 0. Force known_brand_origins if available
    if brand_key in known_brand_origins:
        country = known_brand_origins[brand_key]
        city = origin_hubs.get(country, origin_hubs["UK"])["city"]
        return country, city


    # 1. Direct match in enriched brand_locations
    if brand_key in brand_locations:
        return brand_locations[brand_key]["origin"]["country"], brand_locations[brand_key]["origin"]["city"]

    # 2. Match in brand_origin_lookup CSV
    elif brand_key in brand_origin_lookup:
        return brand_origin_lookup[brand_key]["country"], brand_origin_lookup[brand_key]["city"]

    # 3. Match in hardcoded known_brand_origins
    elif brand_key in known_brand_origins:
        country = known_brand_origins[brand_key]
        city = origin_hubs.get(country, origin_hubs["UK"])["city"]
        return country, city

    # 4. Intelligent brand resolution system (NEW ENHANCED DETECTION)
    else:
        Log.warn(f"⚠️ Unrecognized brand: {brand_key}")
        
        # Try intelligent brand resolution first
        intelligent_result = get_brand_origin_intelligent(
            brand=brand_key, 
            product_title=title_fallback or "",
            additional_context=""
        )
        
        # Use intelligent result if confidence is reasonable
        if intelligent_result["confidence"] >= 0.50:
            country = intelligent_result["country"]
            city = intelligent_result.get("city", "Unknown")
            if city == "Unknown":
                city = origin_hubs.get(country, origin_hubs["UK"])["city"]
            
            brand_locations[brand_key] = {
                "origin": {
                    "country": country,
                    "city": city
                },
                "fulfillment": "UK"
            }
            save_brand_locations()
            Log.success(f"🧠 Intelligent detection: {brand_key} → {country} (confidence: {intelligent_result['confidence']:.2f}, source: {intelligent_result['source']})")
            return country, city
        
        # 5. Fallback to basic title estimation
        elif title_fallback:
            guessed_country = estimate_origin_country(title_fallback)
            guessed_city = origin_hubs.get(guessed_country, origin_hubs["UK"])["city"]
            brand_locations[brand_key] = {
                "origin": {
                    "country": guessed_country,
                    "city": guessed_city
                },
                "fulfillment": "UK"
            }
            save_brand_locations()
            Log.success(f"📦 Basic estimation from title: {brand_key} → {guessed_country}")
            return guessed_country, guessed_city

        # 6. Log unknown brand
        # Ensure unrecognized_brands.txt exists
        if not os.path.exists("unrecognized_brands.txt"):
            with open("unrecognized_brands.txt", "w", encoding="utf-8") as f:
                f.write("")  # create an empty file

        with open("unrecognized_brands.txt", "a", encoding="utf-8") as log:
            log.write(f"{brand_key}\n")
        return "Unknown", "Unknown"
    




def infer_fulfillment_country(url, sold_by_text=""):
    url = url.lower()
    sold_by_text = sold_by_text.lower()
    if "amazon.co.uk" in url or "dispatched from and sold by amazon" in sold_by_text:
        return "UK"
    elif "amazon.de" in url or "versand durch amazon" in sold_by_text:
        return "Germany"
    elif "amazon.fr" in url:
        return "France"
    elif "amazon.it" in url:
        return "Italy"
    elif "amazon.com" in url:
        return "USA"
    return "UK"  # fallback default

def save_brand_locations():
    global brand_locations
    with open("brand_locations.json", "w", encoding="utf-8") as f:
        json.dump(brand_locations, f, indent=2)
        Log.success(f"📦 Saved updated brand_locations.json with {len(brand_locations)} entries.")

def safe_save_brand_origin(brand_key, country, city="Unknown"):
    if not country or country.lower() == "unknown":
        return  # Skip invalid

    current = brand_locations.get(brand_key, {}).get("origin", {})
    current_country = current.get("country", "").lower()

    if current_country != country.lower():
        brand_locations[brand_key] = {
            "origin": {
                "country": country,
                "city": city
            },
            "fulfillment": "UK"
        }
        save_brand_locations()
        Log.success(f"📦 Inferred and saved origin for {brand_key}: {country}")


def enrich_brand_location(brand_name, example_url):
    global brand_locations

    
    driver = webdriver.Chrome(service=Service("C:/Users/jamie/OneDrive/Documents/University/ComputerScience/Year3/DigitalSP/DSProject/Tools/chromedriver-win64/chromedriver.exe"), options=chrome_options)
    driver.get(example_url)

    try:
        text_blobs = []
        legacy_specs = []

        # Try pulling merchant info or description
        try:
            merchant = driver.find_element(By.ID, "merchant-info").text
            text_blobs.append(merchant)
        except:
            pass

        try:
            desc = driver.find_element(By.ID, "productDescription").text
            text_blobs.append(desc)
        except:
            pass

        try:
            bullets = driver.find_elements(By.CSS_SELECTOR, "#feature-bullets li")
            text_blobs += [b.text for b in bullets]
        except:
            pass

        for blob in text_blobs:
            blob = blob.lower()
            if "made in" in blob or "manufactured in" in blob:
                match = re.search(r"(made|manufactured)\s+in\s+([a-z\s,]+)", blob)
                if match:
                    location = match.group(2).strip().title()
                    country = location.split(",")[-1].strip()
                    city = location.split(",")[0].strip() if "," in location else "Unknown"

                    print(f"🔍 Guessed: {brand_name} → {city}, {country}")

                    brand_locations[brand_name] = {
                        "origin": {
                            "country": country,
                            "city": city
                        },
                        "fulfillment": "UK"
                    }
                     # 🚀 Save it instantly
                    save_brand_locations()
                    return

        print(f"❌ No location found for: {brand_name}")

    finally:
        driver.quit()

# Example enrichment script
# Ensure the unrecognized_brands.txt file exists before reading
if not os.path.exists("unrecognized_brands.txt"):
    with open("unrecognized_brands.txt", "w", encoding="utf-8") as f:
        f.write("")  # just creates the file if it doesn't exist

with open("unrecognized_brands.txt", "r", encoding="utf-8") as f:
    brands_to_enrich = set(line.strip() for line in f if line.strip())

# Dummy mapping — replace with real example URLs per brand
example_urls = {
    "anker": "https://www.amazon.co.uk/dp/B09KT1NR6V",
    "huel": "https://www.amazon.co.uk/dp/B0CFQKQNX3",
    "avm": "https://www.amazon.co.uk/dp/B01N8S4URO"
}

def finalize_product_entry(product):
    """
    Ensures product has all required fields: origin, city, weight.
    Enriches brand origin if missing. Updates all product DBs.
    """
    brand_key = product.get("brand", product.get("title", "").split()[0]).lower().strip()
    title = product.get("title", "")
    
    # Resolve missing origin
    if not product.get("brand_estimated_origin") or product["brand_estimated_origin"].lower() in ["unknown", "other", ""]:
        country, city = resolve_brand_origin(brand_key, title)
        product["brand_estimated_origin"] = country
        product["origin_city"] = city

    # Resolve missing weight
    if not product.get("estimated_weight_kg"):
        fallback_weight = extract_weight(title)
        if fallback_weight:
            product["estimated_weight_kg"] = fallback_weight
            Log.warn(f"⚖️ Fallback weight from title: {fallback_weight} kg")

    # Save to cleaned products
    try:
        cleaned_path = "cleaned_products.json"
        if os.path.exists(cleaned_path):
            with open(cleaned_path, "r", encoding="utf-8") as f:
                cleaned = json.load(f)
        else:
            cleaned = []

        cleaned.append(product)
        with open(cleaned_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2)
        Log.success("🧽 Product added to cleaned_products.json")
    except Exception as e:
        Log.warn(f"⚠️ Could not write to cleaned_products.json: {e}")

    # Save to priority products if high quality
    maybe_add_to_priority(product, priority_products)


for brand in brands_to_enrich:
    if brand in example_urls:
        enrich_brand_location(brand, example_urls[brand])

# ✅ Save to JSON here, after loop is complete
with open("brand_locations.json", "w", encoding="utf-8") as f:
    json.dump(brand_locations, f, indent=2)
    Log.success(f"📦 Saved updated brand_locations.json with {len(brand_locations)} entries.")


def extract_recyclability(text_blobs):
    full_text = " ".join(text_blobs).lower()
    if any(kw in full_text for kw in ["100% recyclable", "fully recyclable", "recyclable packaging"]):
        return "High"
    elif any(kw in full_text for kw in ["partially recycled", "made from recycled", "recycled content"]):
        return "Medium"
    elif any(kw in full_text for kw in ["not recyclable", "non-recyclable", "plastic packaging"]):
        return "Low"
    return "Unknown"

def is_invalid_brand(candidate):
    candidate = candidate.lower()
    return (
        candidate in ["usb", "type", "plug", "cable", "portable", "wireless", "eco", "fast", "unknown", "for"]
        or re.match(r"^\d+[a-z]{0,3}$", candidate)
        or candidate.isdigit()
    )

def scrape_amazon_titles(url, max_items=100, enrich=False):
    import undetected_chromedriver as uc
    from common.data.brand_origin_resolver import get_brand_origin, get_brand_origin_intelligent

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

    if not safe_get(driver, url):
        Log.error(f"🛑 Giving up on URL: {url}")
        return []

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-main-slot div[data-asin]"))
        )
    except:
        Log.error("❌ Could not find product containers.")
        driver.quit()
        return []

    time.sleep(2)
    product_elements = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-asin]")
    print(f"🔍 Found {len(product_elements)} items")

    products = []

    for product in product_elements:
        if len(products) >= max_items:
            break

        try:
            asin = product.get_attribute("data-asin")
            if not asin:
                continue

            # === Robust link selector fallback ===
            link_el = None
            for sel in [
                "a.a-link-normal.s-no-outline",
                "h2 a.a-link-normal",
                "a.a-link-normal"
            ]:
                try:
                    link_el = product.find_element(By.CSS_SELECTOR, sel)
                    if link_el:
                        break
                except:
                    continue

            if not link_el:
                Log.warn("⚠️ Skipping: No valid product link found.")
                continue

            href = link_el.get_attribute("href")

            # === Extract title ===
            title = None
            for selector in [
                "span.a-size-medium.a-color-base.a-text-normal",
                "span.a-size-base-plus.a-color-base.a-text-normal",
                "h2 span"
            ]:
                try:
                    title_el = product.find_element(By.CSS_SELECTOR, selector)
                    title = title_el.text.strip()
                    if title:
                        break
                except:
                    continue

            if not title:
                continue

            # === Detect brand ===
            brand = product.get_attribute("data-brand") or None
            if not brand:
                try:
                    el = product.find_element(By.CSS_SELECTOR, "h5.s-line-clamp-1 span.a-size-base")
                    brand = el.text.strip()
                except:
                    pass

            if not brand:
                first_word = title.split()[0].lower()
                brand = first_word.capitalize() if not is_invalid_brand(first_word) else "Unknown"

            brand_key = brand.lower().strip()
            if is_invalid_brand(brand_key):
                Log.warn(f"🚫 Skipping invalid brand: {brand_key}")
                continue

            # === Get or enrich brand origin ===
            origin_info = get_brand_origin(brand_key)
            origin_country = origin_info["country"]
            origin_city = origin_info["city"]

            if origin_country == "Unknown" and enrich:
                enrich_brand_location(brand_key, href)
                origin_info = get_brand_origin(brand_key)
                origin_country = origin_info["country"]
                origin_city = origin_info["city"]

            # === Estimate rest of metadata ===
            fulfillment_country = infer_fulfillment_country(href)
            origin = origin_hubs.get(origin_country, origin_hubs["UK"])
            fulfillment_hub = amazon_fulfillment_centers.get(fulfillment_country, amazon_fulfillment_centers["UK"])
            distance = round(haversine(origin["lat"], origin["lon"], fulfillment_hub["lat"], fulfillment_hub["lon"]), 1)

            full_text = product.text.lower()
            weight = extract_weight(full_text) or extract_weight(title)
            material = extract_material(full_text)

            products.append({
                "asin": asin,
                "title": title,
                "brand_estimated_origin": origin_country,
                "origin_city": origin_city,
                "distance_origin_to_uk": distance,
                "distance_uk_to_user": 100,
                "estimated_weight_kg": weight,
                "co2_emissions": None,
                "material_type": material,
                "recyclability": random.choice(["Low", "Medium", "High"])
            })

        except Exception as e:
            Log.warn(f"⚠️ Skipping product due to error: {e}")

    driver.quit()
    return products



import os

#IS_DOCKER = os.environ.get('IS_DOCKER', 'false').lower() == 'true'
def scrape_amazon_product_page(amazon_url, fallback=False):
    print("🧪 Inside scraper function, fallback mode is:", fallback)

    #if IS_DOCKER:
        #fallback = False
  
    import undetected_chromedriver as uc
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    print("🧪 Inside scraper function, fallback mode is:", fallback)

    if fallback:
        print("🟡 Using fallback mode, returning mock product.")
        return {
            "title": "Test Product (Fallback Mode)",
            "origin": "Unknown",
            "weight_kg": 0.6,
            "dimensions_cm": [20, 10, 5],
            "material_type": "Plastic",
            "recyclability": "Low",
            "eco_score_ml": "F",
            "transport_mode": "Land",
            "carbon_kg": None
        }

    driver = None
    
    
    
    try:
        print("🚀 Launching undetected ChromeDriver...")
        from undetected_chromedriver import Chrome, ChromeOptions
        options = ChromeOptions()
        options.user_data_dir = "selenium_profile"  # Folder to store persistent session/cookies
        driver = Chrome(headless=False, options=options)


        print("🌐 Navigating to page:", amazon_url)
        driver.get(amazon_url)
        driver.implicitly_wait(5)
        
        text_blobs = [] 
        legacy_specs = [] 
        
        
 # === 🛡️ Bot detection handling ===
        page = driver.page_source.lower()
        if "robot check" in page or "captcha" in page:
            print("🛑 CAPTCHA detected! Saving screenshot...")

            driver.save_screenshot("captcha_screenshot.png")
            print("📸 Saved screenshot as captcha_screenshot.png")
            print("🧍 Please solve the CAPTCHA in the Chrome window.")
            input("✅ Press Enter here once you've solved the CAPTCHA and see the product page...")

            print("🔁 Retrying scrape after CAPTCHA solve...")

            # Re-fetch page content after manual solve
            page = driver.page_source.lower()
            if "robot check" in page or "captcha" in page:
                print("❌ CAPTCHA still present after retry. Giving up.")
                return None


        # Bot detection check
        page = driver.page_source.lower()
        if "robot check" in page or "captcha" in page:
            print("🛑 Blocked by CAPTCHA / bot check.")
            return None

        print("🖱️ Simulating scroll + click...")
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
            time.sleep(random.uniform(1, 2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(random.uniform(1.5, 2.5))
        except Exception as e:
            print(f"⚠️ Scroll simulation failed: {e}")

        # Try to expand spec blocks
        try:
            expandable = driver.find_elements(By.CSS_SELECTOR, ".a-expander-header")
            if expandable:
                random.choice(expandable).click()
                time.sleep(random.uniform(1, 2))
        except:
            pass

        # Hover over title
        try:
            hover_target = driver.find_element(By.ID, "productTitle")
            webdriver.ActionChains(driver).move_to_element(hover_target).perform()
            time.sleep(random.uniform(0.5, 1.2))
        except:
            pass

        # Wait and parse title
        title = None
        selectors = [
            (By.ID, "productTitle"),
            (By.CSS_SELECTOR, "#title span"),
            (By.CSS_SELECTOR, "span#productTitle"),
            (By.CSS_SELECTOR, "h1.a-size-large span")
        ]
        for by, selector in selectors:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, selector)))
                title = driver.find_element(by, selector).text.strip()
                break
            except:
                continue

        if not title:
            print(f"❌ Failed to extract product title for: {amazon_url}")
            return None

        asin = extract_asin(amazon_url)
        if asin in priority_products:
            Log.success("🎯 Using locked metadata for high-accuracy product.")
            return priority_products[asin]

        try:
            brand = driver.find_element(By.ID, "bylineInfo").text.strip()
        except:
            brand = title.split()[0]

        def normalize_brand(brand_raw):
            return brand_raw.lower().replace("visit the", "").replace("store", "").strip()

        # Use it like this:
        brand_name = normalize_brand(brand)
        brand_key = brand_name  # already normalized

        print("🧾 Raw brand text:", brand_name)


        if brand_key not in brand_origin_lookup and brand_key not in known_brand_origins:
            # Ensure the file exists
            if not os.path.exists("unrecognized_brands.txt"):
                with open("unrecognized_brands.txt", "w", encoding="utf-8") as f:
                    f.write("")  # create an empty file

            with open("unrecognized_brands.txt", "a", encoding="utf-8") as log:
                log.write(f"{brand_name}\n")

        if brand_key not in brand_locations:
            enrich_brand_location(brand_name, amazon_url)

        # === ORIGIN PRIORITY: Structured page data > unstructured page > brand DB > defaults
        origin_country = "Unknown"
        origin_city = "Unknown"
        origin_source = "Unknown"
        origin_confidence = "unknown"

        # STEP 1: Extract from structured Amazon sections FIRST (highest priority)
        origin_data = extract_origin_from_structured_data(driver)
        if origin_data["found"]:
            origin_country = origin_data["country"]
            origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
            origin_source = "structured_page_data"
            origin_confidence = "high"
            print(f"🎯 HIGH CONFIDENCE origin from structured data: {origin_country}")
        
        # STEP 2: Only try unstructured extraction if no structured data found
        elif origin_country in ["Unknown", "Other", None, ""]:

            # 1. Try to extract origin from page blobs
            for blob in text_blobs:
                legacy_specs = []
                if any(kw in blob for kw in ["country of origin", "made in", "manufacturer"]):
                    # Enhanced regex patterns for different Amazon formats
                    origin_patterns = [
                        r"country\s+of\s+origin[:\s]*([a-zA-Z\s,]+)",  # "Country of origin: Vietnam"
                        r"origin[:\s]*([a-zA-Z\s,]+)",  # "Origin: Vietnam"
                        r"made\s+in[:\s]*([a-zA-Z\s,]+)",  # "Made in Vietnam"
                        r"manufacturer(?:ed)?\s+in[:\s]*([a-zA-Z\s,]+)",  # "Manufactured in Vietnam"
                        r"product\s+of[:\s]*([a-zA-Z\s,]+)"  # "Product of Vietnam"
                    ]
                    
                    for pattern in origin_patterns:
                        match = re.search(pattern, blob, re.IGNORECASE)
                        if match:
                            raw_origin = match.group(1).strip()
                            # Clean up common trailing words
                            raw_origin = re.sub(r'\s+(and|or|the|other|countries|regions?).*$', '', raw_origin, flags=re.IGNORECASE)
                            if raw_origin.lower() not in ["no", "not specified", "unknown", "", "n/a"]:
                                origin_country = fuzzy_normalize_origin(raw_origin)
                                origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                                origin_source = "blob_match"
                                print(f"📍 Extracted origin from blob: '{raw_origin}' → {origin_country} (pattern: {pattern})")
                                break
                    
                    if origin_country not in ["Unknown", "Other", None, ""]:
                        break

            # 1.5 Check legacy tech specs
            if origin_country in ["Unknown", "Other", None, ""]:
                try:
                    for i in range(len(legacy_specs) - 1):
                        label = legacy_specs[i].text.lower().strip()
                        value = legacy_specs[i + 1].text.strip()
                        if "country of origin" in label:
                            origin_country = fuzzy_normalize_origin(value)
                            origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                            origin_source = "techspec_origin"
                            print(f"📍 Found origin in tech spec: {value} → {origin_country}")
                            break
                except Exception as e:
                    Log.warn(f"⚠️ Error checking tech spec for origin: {e}")
                    
            # 1.5.2 Extended blob fallback: broader keyword match
            if origin_country in ["Unknown", "Other", None, ""]:
                for blob in text_blobs:
                    if any(kw in blob.lower() for kw in ["country of origin", "made in", "product of", "manufactured in", "origin:", "vietnam", "china", "germany", "usa"]):
                        # Better patterns for different origin formats
                        origin_patterns = [
                            r"country\s+of\s+origin[:\s]*([a-zA-Z\s,]+)",
                            r"made\s+in[:\s]*([a-zA-Z\s,]+)",
                            r"product\s+of[:\s]*([a-zA-Z\s,]+)",
                            r"manufactured\s+in[:\s]*([a-zA-Z\s,]+)",
                            r"origin[:\s]*([a-zA-Z\s,]+)",
                            # Direct country match when keywords like 'vietnam' appear
                            r"\b(vietnam|china|germany|usa|japan|france|italy|uk|united kingdom|thailand|indonesia)\b"
                        ]
                        
                        for pattern in origin_patterns:
                            match = re.search(pattern, blob, re.IGNORECASE)
                            if match:
                                raw_origin = match.group(1).strip()
                                # Clean up trailing words and punctuation
                                raw_origin = re.sub(r'\s+(and|or|the|other|countries|regions?|etc).*$', '', raw_origin, flags=re.IGNORECASE)
                                raw_origin = re.sub(r'[,;.].*$', '', raw_origin).strip()
                                
                                if raw_origin and raw_origin.lower() not in ["unknown", "not specified", "", "n/a", "other"]:
                                    origin_country = fuzzy_normalize_origin(raw_origin)
                                    origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                                    origin_source = "blob_fallback"
                                    print(f"🌍 Extracted origin from extended blob: '{raw_origin}' → {origin_country} (pattern: {pattern})")
                                    break
                        if origin_country not in ["Unknown", "Other", None, ""]:
                            break


            # 2. Fallback: brand DB, but only if page didn’t already give a specific origin
            if origin_country in ["Unknown", "Other", None, ""]:
                print("⚠️ No page origin data found - using brand intelligence...")
                brand_intel = get_brand_intelligent_origin(brand_key, title)
                
                if brand_intel["country"] != "Unknown":
                    origin_country = brand_intel["country"]
                    origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                    origin_source = "brand_intelligence"
                    origin_confidence = brand_intel["confidence"]
                    print(f"🧠 Brand intelligence: {brand_intel['reasoning']}")
                else:
                    # Final fallback to generic brand DB
                    db_origin_country, db_origin_city = resolve_brand_origin(brand_key, title)
                    origin_country = db_origin_country
                    origin_city = db_origin_city
                    origin_source = "brand_db_generic"
                    origin_confidence = "low"
                    print(f"📚 Generic brand fallback: {brand_key} → {origin_country}")
            else:
                print(f"🛡️ Preserving explicit product origin: {origin_country} (source: {origin_source})")

            # 3. Fallback: title guess
            if origin_country in ["Unknown", "Other", None, ""] and origin_source not in ["brand_db", "blob_match", "techspec_origin"]:
                origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                origin_source = "title_guess"
                print(f"🧠 Fallback origin estimate from title: {guess}")
            else:
                print(f"🚫 Skipping fallback origin guess — origin already resolved from {origin_source}")


            # 4. Final fallback: shipping panel
            if origin_country in ["Unknown", "Other", None, ""]:
                guess = extract_shipping_origin(driver)
                if guess:
                    origin_country = fuzzy_normalize_origin(guess)
                    origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                    origin_source = "shipping_panel"
                    print(f"🚚 Inferred origin from shipping panel: {guess}")
                    
            # 🛡️ Final fallback override guard to protect brand DB origin
            if origin_source == "brand_db":
                origin_country = known_brand_origins.get(brand_key, origin_country)
                origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                print(f"🛡️ Protected origin override — sticking with brand DB: {origin_country}")

            # Apply intelligent validation before finalizing
            validated_origin, validated_city, validated_source, validated_confidence = apply_validation_to_origin_detection(
                origin_country, origin_source, brand_key, title
            )
            
            origin_country = validated_origin
            origin_city = validated_city 
            origin_source = validated_source
            origin_confidence = validated_confidence
            
            print(f"🎯 Final validated origin: {origin_country} (source: {origin_source}, confidence: {origin_confidence})")

            # 🛡️ Final override protection
            if asin in priority_products:
                origin_country = priority_products[asin].get("brand_estimated_origin", origin_country)
                origin_city = priority_products[asin].get("origin_city", origin_city)
                print(f"🔒 Restored origin from priority DB: {origin_country}")

        else:
            print(f"🌍 Skipping all fallbacks — origin already set to: {origin_country} (source: {origin_source})")


        # === STRUCTURED DATA EXTRACTION (HIGH PRIORITY) ===
        # Extract weight with confidence tracking
        weight_data = extract_weight_from_structured_data(driver)
        if weight_data["found"]:
            weight = weight_data["weight_kg"]
            weight_confidence = "high"
            weight_source = weight_data["method"]
            print(f"⚖️ HIGH CONFIDENCE weight: {weight}kg (source: {weight_source})")
        else:
            weight = None
            weight_confidence = "unknown"
            weight_source = "none"
        
        # Extract materials with multi-material support
        materials_data = extract_materials_from_structured_data(driver)
        if materials_data["found"]:
            all_materials = materials_data["materials"]
            primary_material = materials_data["primary_material"]
            material_confidence = "high" if any(m["confidence"] == "high" for m in all_materials) else "medium"
            material_source = materials_data["method"]
            
            # Log all materials found
            material_names = [m["name"] for m in all_materials]
            print(f"🧬 {material_confidence.upper()} CONFIDENCE materials: {', '.join(material_names)} (primary: {primary_material})")
            material_breakdown = [f"{m['name']} ({m['weight']:.1%})" for m in all_materials]
            print(f"📊 Material breakdown: {material_breakdown}")
            
            material = primary_material  # For backwards compatibility
        else:
            all_materials = []
            primary_material = None
            material = None
            material_confidence = "unknown"
            material_source = "none"
        
        # Extract dimensions (keep existing logic for now)
        dimensions = None
        recyclability = None
        recyclability_percentage = 30  # Default fallback
        recyclability_desc = "Recyclability assessment pending"
        try:
            text_blobs = []
            legacy_specs = []

            bullets = driver.find_elements(By.CSS_SELECTOR, "#detailBullets_feature_div li")
            kv_rows = driver.find_elements(By.CSS_SELECTOR, "table.a-keyvalue tr")
            desc = driver.find_elements(By.ID, "productDescription")

            # ✅ Safe default + attempt to assign if possible
            legacy_specs = []
            try:
                legacy_specs = driver.find_elements(By.CSS_SELECTOR, "#productDetails_techSpec_section_1 td")
            except:
                pass

            # 📦 Now collect all into text_blobs
            text_blobs += [b.text.strip().lower() for b in bullets]
            text_blobs += [r.text.strip().lower() for r in kv_rows]
            text_blobs += [l.text.strip().lower() for l in legacy_specs]
            text_blobs += [d.text.strip().lower() for d in desc]

            print("🔍 Starting to parse text blobs for product details...")

            
            origin_already_saved = False  # ✅ Add this before the loop
            
            bullets = driver.find_elements(By.CSS_SELECTOR, "#detailBullets_feature_div li")
            kv_rows = driver.find_elements(By.CSS_SELECTOR, "table.a-keyvalue tr")
            desc = driver.find_elements(By.ID, "productDescription")

            text_blobs += [b.text.strip().lower() for b in bullets]
            text_blobs += [r.text.strip().lower() for r in kv_rows]
            text_blobs += [d.text.strip().lower() for d in desc]

            material = None
            material_source = "Unknown"


            for blob in text_blobs:
                legacy_specs = []
                if not weight and any(kw in blob for kw in ["weight", "weighs", "item weight", "product weight"]):
                    extracted_weight = extract_weight(blob)
                    if extracted_weight:
                        weight = extracted_weight
                        print(f"⚖️ Extracted weight: {weight} kg")

                if not weight:
                    extracted_weight = extract_weight(title)
                    if extracted_weight:
                        weight = extracted_weight
                        print(f"⚠️ Extracted from title fallback: {weight} kg")

                if not dimensions:
                    extracted_dimensions = extract_dimensions(blob)
                    if extracted_dimensions:
                        dimensions = extracted_dimensions
                        print(f"📦 Extracted dimensions: {dimensions} cm")


              

                # === MATERIAL INFERENCE LOGIC ===
                def infer_material(title, text_blobs, asin=None):
                    material = None
                    material_source = "Unknown"

                    # Flatten and lowercase all text blobs
                    all_text = " ".join(text_blobs).lower()
                    title = title.lower()

                    # 1. Direct keyword match (text blobs)
                    keyword_map = {
                        "Plastic": ["plastic", "polypropylene", "pp", "polyethylene", "pet"],
                        "Glass": ["glass", "borosilicate"],
                        "Aluminium": ["aluminium", "aluminum"],
                        "Steel": ["steel", "stainless steel", "inox"],
                        "Paper": ["paper", "paperboard"],
                        "Cardboard": ["cardboard", "carton"],
                        "Fabric": ["fabric", "cloth", "textile", "canvas"],
                        "Cotton": ["cotton"],
                        "Bamboo": ["bamboo"],
                        "Wood": ["wood", "wooden"],
                        "Rubber": ["rubber"],
                        "Silicone": ["silicone"]
                    }

                    for mat, terms in keyword_map.items():
                        if any(kw in all_text for kw in terms):
                            material = mat
                            material_source = "text_blob_match"
                            break

                    # 2. Fuzzy fallback using title
                    if not material or material.lower() == "unknown":
                        for mat, terms in keyword_map.items():
                            if any(kw in title for kw in terms):
                                material = mat
                                material_source = "title_fuzzy"
                                break

                    # 3. Category heuristics
                    category_keywords = {
                        "Paper": ["card", "board game", "book", "journal", "notebook", "diary", "pad"],
                        "Plastic": ["tablet", "tub", "bottle", "container", "cap", "case", "lid", "pouch", "tube"],
                        "Glass": ["jar", "flask", "mason"],
                        "Fabric": ["bag", "tote", "backpack"],
                        "Steel": ["thermos", "cutlery", "knife", "fork", "bottle opener"],
                    }
                    if not material or material.lower() == "unknown":
                        for mat, keywords in category_keywords.items():
                            if any(word in title for word in keywords):
                                material = mat
                                material_source = "category_guess"
                                break

                    # 4. Similar ASIN lookup (if priority DB available)
                    if not material and asin and asin in priority_products:
                        trusted_product = priority_products[asin]
                        mat = trusted_product.get("material_type")
                        if mat and mat.lower() not in ["unknown", ""]:
                            material = mat
                            material_source = "trusted_db"

                    # 5. Final fallback
                    if not material:
                        material = "Unknown"
                        material_source = "default"

                    return material, material_source

                # Inject this into your scrape_amazon_product_page logic around material inference:
                # Replace your entire material detection block with:
                material, material_source = infer_material(title, text_blobs, asin)
                print(f"🧬 Final inferred material: {material} (source: {material_source})")

                    

                # === RECYCLABILITY ESTIMATION ===
                material_recyclability_map = {
                    "plastic": "Medium",
                    "glass": "High",
                    "aluminium": "High",
                    "steel": "High",
                    "paper": "Medium",
                    "cardboard": "Medium",
                    "fabric": "Low",
                    "cotton": "Low",
                    "bamboo": "Low",
                    "wood": "Low"
                }

                # Skip smart recyclability here - will be done after loop completes



                # ✅ Save brand origin only ONCE
                if not origin_already_saved:
                    safe_save_brand_origin(brand_key, origin_country, origin_city)
                    origin_already_saved = True

                if weight and dimensions and material and origin_country:
                    print("✅ All key details found.")
                    break
                
                
            # === MATERIAL FALLBACK LOGIC ===
            # Only try text-based material extraction if structured extraction failed
            if not material:
                print("⚠️ No material found in structured data - trying text blob extraction...")
                for blob in text_blobs:
                    if any(kw in blob for kw in ["material", "sole", "outer", "fabric"]):
                        extracted_material = extract_material(blob)
                        if extracted_material and extracted_material != "Unknown":
                            material = extracted_material
                            material_confidence = "medium"
                            material_source = "text_blob_fallback"
                            print(f"🧬 MEDIUM CONFIDENCE material from text: {material}")
                            break
            
            # Don't guess materials - better to be honest about uncertainty
            if not material:
                material = "Unknown"
                material_confidence = "unknown"
                material_source = "none_found"
                print(f"🧬 No material information found - setting as Unknown")

            # === COMPOUND RECYCLABILITY CALCULATION ===
            # Calculate recyclability based on all materials found (compound analysis)
            if all_materials:
                recyclability_level, recyclability_percentage, recyclability_desc = calculate_compound_recyclability(all_materials)
                recyclability = recyclability_level
                
                # Adjust confidence based on material confidence
                if material_confidence == "high":
                    recyclability_confidence = "high"
                elif material_confidence == "medium":
                    recyclability_confidence = "medium"
                else:
                    recyclability_confidence = "low"
                    
                print(f"♻️ Compound recyclability analysis: {recyclability} ({recyclability_percentage}%) - {recyclability_desc} [confidence: {recyclability_confidence}]")
            elif material and material != "Unknown":
                # Fallback to single material calculation
                recyclability_level, recyclability_percentage, recyclability_desc = calculate_smart_recyclability(material)
                recyclability = recyclability_level
                recyclability_confidence = "medium"
                print(f"♻️ Single material recyclability: {material} → {recyclability} ({recyclability_percentage}%) - {recyclability_desc}")
            else:
                # No material data available
                recyclability = "Unknown"
                recyclability_percentage = 0
                recyclability_desc = "Cannot assess recyclability without material identification"
                recyclability_confidence = "unknown"
                print(f"♻️ Cannot calculate recyclability - no material data available")

        except Exception as e:
            print("⚠️ Extraction error:", e)

        # === INTELLIGENT FALLBACKS (only when structured extraction fails) ===
        # Weight fallback: Only use generic fallback if NO weight found anywhere
        if not weight:
            print("⚠️ No weight found in structured data - trying text blob extraction...")
            # Try old extraction method as fallback
            for blob in text_blobs:
                if any(kw in blob for kw in ["weight", "weighs", "item weight"]):
                    extracted_weight = extract_weight(blob)
                    if extracted_weight:
                        weight = extracted_weight
                        weight_confidence = "medium"
                        weight_source = "text_blob_fallback"
                        print(f"⚖️ MEDIUM CONFIDENCE weight from text: {weight}kg")
                        break
        
        # Final weight fallback: Only use 1kg default if absolutely nothing found
        if not weight:
            print("⚠️ No weight found anywhere - using category-based fallback")
            # TODO: Could implement category-specific defaults here
            weight = 1.0
            weight_confidence = "low"
            weight_source = "generic_default"

        # ✅ Only use shipping panel if origin is still unknown
        if origin_country in ["Unknown", "Other", None, ""]:
            guess = extract_shipping_origin(driver)
            if guess:
                origin_country = fuzzy_normalize_origin(guess)
                origin_city = origin_hubs.get(origin_country, {}).get("city", "Unknown")
                origin_source = "shipping_panel"
                print(f"🚚 Inferred origin from shipping panel: {guess}")
        else:
            print(f"🛡️ Protected origin: {origin_country} (source: {origin_source})")


        origin_hub = origin_hubs.get(origin_country, origin_hubs["UK"])
        distance = round(haversine(origin_hub["lat"], origin_hub["lon"], uk_hub["lat"], uk_hub["lon"]), 1)

            # === Infer smarter transport mode
        long_distance_countries = ["China", "USA", "Japan"]
        if origin_country in long_distance_countries:
            transport_mode = "Ship"
        elif origin_country == "UK":
            transport_mode = "Land"
        else:
            transport_mode = "Air"

        

        # === ✅ Fuzzy corrections for material and origin (place it HERE)
        if material:
            mat = material.lower()
            if "plastic" in mat:
                material = "Plastic"
            elif "glass" in mat:
                material = "Glass"
            elif "alum" in mat:
                material = "Aluminium"
            elif "steel" in mat:
                material = "Steel"
            elif "paper" in mat:
                material = "Paper"
            elif "cardboard" in mat:
                material = "Cardboard"

        if origin_country:
            orig = origin_country.lower()
            if "china" in orig:
                origin_country = "China"
            elif "united kingdom" in orig or "uk" in orig:
                origin_country = "UK"
            elif "usa" in orig or "united states" in orig:
                origin_country = "USA"
            elif "germany" in orig:
                origin_country = "Germany"
            elif "france" in orig:
                origin_country = "France"
            elif "italy" in orig:
                origin_country = "Italy"


        # 🔒 Final override if product is in trusted DB
        if asin in priority_products:
            trusted = priority_products[asin]
            origin_country = trusted.get("brand_estimated_origin", origin_country)
            origin_city = trusted.get("origin_city", origin_city)
            print(f"🔒 Final override from priority DB: {origin_country}")
            
        # === DATA PROVENANCE SUMMARY ===
        print("\n🔍 === EXTRACTION SUMMARY ===")
        print(f"📍 Origin: {origin_country} (source: {origin_source}, confidence: {origin_confidence})")
        print(f"⚖️ Weight: {weight}kg (source: {weight_source}, confidence: {weight_confidence})")  
        
        # Enhanced material summary
        if all_materials and len(all_materials) > 1:
            material_summary = f"Primary: {primary_material} | All: {', '.join([m['name'] for m in all_materials])}"
            print(f"🧬 Materials: {material_summary} (source: {material_source}, confidence: {material_confidence})")
        else:
            print(f"🧬 Material: {material} (source: {material_source}, confidence: {material_confidence})")
        
        print(f"♻️ Recyclability: {recyclability} ({recyclability_percentage}%) - {recyclability_desc}")
        print("================================\n")

        # Calculate distance here before assigning to product
        origin_hub = origin_hubs.get(origin_country, origin_hubs["UK"])
        distance_origin_to_uk = round(haversine(origin_hub["lat"], origin_hub["lon"], uk_hub["lat"], uk_hub["lon"]), 1)
        distance_uk_to_user = 100

        # === Now build your product dict (after fuzzy fixes)
        
        # === CO2 emissions estimate using material_co2_map
        co2_emissions = None
        if material and weight:
            co2_emissions = round(material_co2_map.get(material.lower(), 2.0) * weight, 2)
            
        
            

        # === Calculate overall confidence based on data sources ===
        confidence_scores = {
            "high": 3,
            "medium": 2, 
            "low": 1,
            "unknown": 0
        }
        
        total_confidence = (
            confidence_scores.get(origin_confidence, 0) +
            confidence_scores.get(weight_confidence, 0) +
            confidence_scores.get(material_confidence, 0)
        ) / 3
        
        if total_confidence >= 2.5:
            overall_confidence = "High"
        elif total_confidence >= 1.5:
            overall_confidence = "Medium"
        elif total_confidence >= 0.5:
            overall_confidence = "Low"
        else:
            overall_confidence = "Estimated"

        product = {
            "asin": asin,
            "title": title,
            "brand_estimated_origin": origin_country,
            "origin_city": origin_city,
            "distance_origin_to_uk": distance_origin_to_uk,
            "distance_uk_to_user": 100,
            "estimated_weight_kg": round(weight * 1.05, 2),
            "raw_product_weight_kg": weight,
            "dimensions_cm": dimensions,
            "material_type": material,  # Keep for backwards compatibility
            "co2_emissions": None,
            "recyclability": recyclability,
            "recyclability_percentage": recyclability_percentage,
            "recyclability_description": recyclability_desc,
            "transport_mode": transport_mode,
            "co2_emissions": co2_emissions,
            "confidence": overall_confidence,
            # === NEW: Enhanced material information ===
            "materials": {
                "primary_material": primary_material or material,
                "all_materials": [{"name": m["name"], "weight": m["weight"]} for m in all_materials] if all_materials else [],
                "material_count": len(all_materials) if all_materials else (1 if material != "Unknown" else 0)
            },
            # === NEW: Data provenance metadata ===
            "data_sources": {
                "origin_source": origin_source,
                "origin_confidence": origin_confidence,
                "weight_source": weight_source,
                "weight_confidence": weight_confidence,
                "material_source": material_source,
                "material_confidence": material_confidence
            }
        }
        
        
        # ✅ Now process + store it
        finalize_product_entry(product)
        return product


        # 🌍 Add missing distance fields
        origin_hub = origin_hubs.get(origin_country, origin_hubs["UK"])
        distance_origin_to_uk = round(haversine(origin_hub["lat"], origin_hub["lon"], uk_hub["lat"], uk_hub["lon"]), 1)
        distance_uk_to_user = 100  # static fallback — change if postcode logic is added

        product["distance_origin_to_uk"] = distance_origin_to_uk
        product["distance_uk_to_user"] = distance_uk_to_user
        print(f"🌍 Returning distances: {product.get('distance_origin_to_uk')} km from origin, {product.get('distance_uk_to_user')} km from UK hub")


        print("✅ Scraped product:", product["title"])
        print(f"🎯 Returning final origin: {origin_country} (source: {origin_source})")
        return product



    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass



# === SAVE TO FILE ===
def save_products_to_json(products, path="../ReactPopup/public/data.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)
    print(f"✅ Saved {len(products)} product(s) to {path}")

# === MAIN ===
if __name__ == "__main__":
    all_asins = set()
    all_products = []

    # Load priority DB
    priority_path = "priority_products.json"
    try:
        with open(priority_path, "r", encoding="utf-8") as f:
            priority_db = json.load(f)
            Log.success(f"🔐 Loaded {len(priority_db)} priority products.")
    except:
        priority_db = {}
        Log.warn("No existing priority_products.json, starting fresh.")

    # Define search terms
    search_terms = [
        "usb+c+charger", "eco+friendly+bottle", "coffee+mug", "mechanical+keyboard", 	
        "shampoo", "wireless+earbuds", "reusable+bag", "portable+fan", "toothbrush", 	
        "led+lamp", "bamboo+cutlery", "compostable+bag", "metal+straw", "plastic+container",
        "fabric+tote", "glass+bottle", "stainless+steel+mug", "wooden+spoon",
        "eco+friendly+notebooks", "recycled+stationery", "canvas+shopping+bag",
        "solar+power+bank", "eco+friendly+phone+case" ,"stainless+steel+lunchbox",
        "reusable+baking+mat", "recycled+paper+towels", "compost+bin+kitchen", 
        "refillable+deodorant", "eco+friendly+shampoo", "solid+shampoo+bar", "bamboo+razor",
        "sustainable+soap", "bamboo+toothbrush", "reusable+straws", "organic+cotton+bag", 
        "biodegradable+cutlery", "eco+cleaning+products", "zero+waste+kit", "reusable+water+bottle",
        "natural+deodorant", "eco+friendly+detergent", "sustainable+kitchen+items", "organic+cotton+towel",
        "eco+friendly+makeup+remover", "reusable+produce+bags", "biodegradable+trash+bags",
        "eco+friendly+gift+wrap", "bamboo+hairbrush", "eco+friendly+dish+soap", "plastic+free+toothpaste",
        "stainless+steel+straws", "eco+friendly+cutting+board", "sustainable+lunch+box",
        "organic+cotton+napkins", "compostable+coffee+pods", "plastic+bottle", "metal+chair", 
        "folding+chair", "water+bottle", "kitchen+knife",
        "cutting+board", "plastic+storage+box", "razor", "electric+shaver", "manual+toothbrush",
        "electric+toothbrush", "bath+towel", "dish+soap", "hand+soap", "laundry+detergent",
        "shower+gel", "body+wash", "reusable+coffee+cup", "travel+mug", "ceramic+mug",
        "kitchen+tongs", "nonstick+pan", "cast+iron+skillet", "kitchen+bin", "recycling+bin",
        "desk+lamp", "office+chair", "monitor+stand", "keyboard", "mouse", "extension+lead",
        "phone+charger", "usb+hub", "batteries", "power+strip", "light+bulb"
    ]


    for term in search_terms:
        for page in range(1, 3):
            url = f"https://www.amazon.co.uk/s?k={term}&page={page}"
            Log.info(f"Scraping: {url}")
            products = scrape_amazon_titles(url, max_items=50)

            new_products = []
            for p in products:
                asin = p.get("asin")
                if asin and asin not in all_asins:
                    all_asins.add(asin)
                    new_products.append(p)
            
            #

            if new_products:
                all_products.extend(new_products)
                Log.success(f"➕ {len(new_products)} new products")

                for p in new_products:
                    asin = p.get("asin")
                    maybe_add_to_priority(p, priority_db)
                    Log.success(f"⭐ Added high-confidence product: {asin}")

                # ✅ Save after each batch of new products
                with open(priority_path, "w", encoding="utf-8") as f:
                    json.dump(priority_db, f, indent=2)
                    Log.success(f"✅ Saved {len(priority_db)} total trusted products.")

                with open("scraped_products_tmp.json", "w", encoding="utf-8") as f:
                    json.dump(all_products, f, indent=2)
                    Log.info(f"📥 Saved checkpoint: {len(all_products)} total")


        time.sleep(random.uniform(2.5, 4.5))  # anti-bot pause

    # ✅ ✅ NOW PROCESS THE PRODUCTS
    unique_products = {p["asin"]: p for p in all_products}.values()

    cleaned_products = []
    for product in unique_products:
        if is_high_confidence(product):
            cleaned_products.append({
                "title": product.get("title"),
                "material": product.get("material_type", "Other"),
                "weight": product.get("estimated_weight_kg", 0.5),
                "transport": product.get("transport_mode", "Land"),
                "recyclability": product.get("recyclability", "Medium"),
                "true_eco_score": "C",  # placeholder
                "co2_emissions": "",
                "origin": product.get("brand_estimated_origin", "Other")
            })

    with open("cleaned_products.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_products, f, indent=2)
        print(f"✅ Saved {len(cleaned_products)} to cleaned_products.json")

    if cleaned_products:
        import csv
        csv_path = os.path.join("ml_model", "real_scraped_dataset.csv")
        with open(csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cleaned_products[0].keys())
            writer.writeheader()
            writer.writerows(cleaned_products)
            print(f"📄 Saved structured training data to {csv_path}")

    save_products_to_json(list(unique_products), "bulk_scraped_products.json")


def calculate_smart_recyclability(material, product_category=None):
    """
    Calculate recyclability score based on material type and product category.
    Returns tuple of (recyclability_level, percentage, description)
    """
    if not material:
        return "Unknown", 30, "Material type not specified"
    
    material = material.lower()
    
    # Material-based recyclability mapping (updated with realistic percentages)
    recyclability_map = {
        # High recyclability (70-90%)
        "aluminum": ("High", 90, "Infinitely recyclable metal - most valuable recyclable"),
        "steel": ("High", 85, "Highly recyclable metal with strong demand"),
        "glass": ("High", 80, "Infinitely recyclable when sorted by color"),
        "paper": ("High", 75, "Widely recyclable when clean and dry"),
        "cardboard": ("High", 88, "Highly recyclable packaging material"),
        
        # Medium recyclability (40-70%)
        "plastic": ("Medium", 55, "Recyclability varies by plastic type (1-7)"),
        "polyethylene": ("Medium", 65, "PE plastic commonly recycled"),
        "polypropylene": ("Medium", 60, "PP plastic recyclable in many programs"), 
        "cotton": ("Medium", 50, "Recyclable through textile programs"),
        "polyester": ("Medium", 45, "Can be recycled into new fibers"),
        "mesh": ("Medium", 40, "Depends on material composition"),
        "fabric": ("Medium", 35, "Textile recycling programs expanding"),
        "canvas": ("Medium", 40, "Natural fiber canvas more recyclable"),
        "synthetic": ("Medium", 30, "Synthetic materials harder to recycle"),
        
        # Low recyclability (10-40%)
        "rubber": ("Low", 20, "Limited recycling - mainly downcycled to mats/mulch"),
        "silicone": ("Low", 15, "Specialized recycling required - very limited"),
        "nylon": ("Low", 25, "Chemical recycling emerging but limited"),
        "leather": ("Low", 10, "Not traditionally recyclable - biodegradable"),
        "foam": ("Low", 12, "Difficult to recycle - mainly energy recovery"),
        
        # Mixed/Unknown materials (medium-low)
        "compound": ("Low", 25, "Mixed materials difficult to separate and recycle"),
        "composite": ("Low", 15, "Multi-material composites very hard to recycle"),
        "mixed": ("Medium", 30, "Depends on component separation feasibility"),
        "textile": ("Medium", 35, "Growing textile recycling infrastructure"),
        "unknown": ("Unknown", 20, "Cannot assess without material identification"),
    }
    
    # Check for exact matches first
    for mat_key, (level, percentage, desc) in recyclability_map.items():
        if mat_key in material:
            return level, percentage, desc
    
    # Default fallback based on common material types
    if any(term in material for term in ["metal", "alumin", "steel"]):
        return "High", 80, "Metal-based materials are typically recyclable"
    elif any(term in material for term in ["plastic", "poly"]):
        return "Medium", 50, "Plastic recyclability varies by type"
    elif any(term in material for term in ["fabric", "textile", "cloth"]):
        return "Medium", 40, "Textile recycling programs available"
    else:
        return "Unknown", 30, "Recyclability assessment requires more material details"


