"""
Most efficient prediction method for Environmental Tracker
Uses the optimized XGBoost model with proper feature engineering
"""

import pandas as pd
import xgboost as xgb
import joblib
import os
import numpy as np

class EfficientEcoPredictor:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.load_model_and_encoders()
    
    def load_model_and_encoders(self):
        """Load the most efficient XGBoost model and encoders"""
        try:
            # Try to load from training directory first (most up-to-date)
            script_dir = os.path.dirname(__file__)
            model_dir = os.path.join(script_dir, "..", "training", "ml_model")
            
            if os.path.exists(model_dir):
                print(f"📁 Loading model from training directory: {model_dir}")
                self.model = xgb.Booster()
                self.model.load_model(os.path.join(model_dir, "xgb_model.json"))
                
                encoders_dir = os.path.join(model_dir, "xgb_encoders")
                self.encoders = {
                    'material': joblib.load(os.path.join(encoders_dir, "material_encoder.pkl")),
                    'transport': joblib.load(os.path.join(encoders_dir, "transport_encoder.pkl")),
                    'recyclability': joblib.load(os.path.join(encoders_dir, "recyclability_encoder.pkl")),
                    'origin': joblib.load(os.path.join(encoders_dir, "origin_encoder.pkl")),
                    'label': joblib.load(os.path.join(encoders_dir, "label_encoder.pkl"))
                }
                print("✅ Loaded efficient XGBoost model and encoders")
                return
            
            # Fallback to main models directory
            model_dir = os.path.join(script_dir, "..", "models")
            if os.path.exists(model_dir):
                print(f"📁 Fallback: Loading model from models directory: {model_dir}")
                self.model = xgb.Booster()
                self.model.load_model(os.path.join(model_dir, "xgb_model.json"))
                
                encoders_dir = os.path.join(script_dir, "..", "encoders")
                self.encoders = {
                    'material': joblib.load(os.path.join(encoders_dir, "material_encoder.pkl")),
                    'transport': joblib.load(os.path.join(encoders_dir, "transport_encoder.pkl")),
                    'recyclability': joblib.load(os.path.join(encoders_dir, "recycle_encoder.pkl")),
                    'origin': joblib.load(os.path.join(encoders_dir, "origin_encoder.pkl")),
                    'label': joblib.load(os.path.join(encoders_dir, "label_encoder.pkl"))
                }
                print("✅ Loaded fallback XGBoost model and encoders")
                return
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def safe_encode(self, value, encoder_name, default_value=None):
        """Safely encode a value using the specified encoder"""
        if encoder_name not in self.encoders:
            raise ValueError(f"Encoder '{encoder_name}' not found")
        
        encoder = self.encoders[encoder_name]
        
        # Clean and normalize the value
        if isinstance(value, str):
            value = value.strip().title()
        
        # Check if value is in encoder classes
        if value not in encoder.classes_:
            if default_value and default_value in encoder.classes_:
                print(f"⚠️ '{value}' not found in {encoder_name} encoder. Using default: '{default_value}'")
                value = default_value
            else:
                # Find the closest match or use the first available class
                available_classes = list(encoder.classes_)
                print(f"⚠️ '{value}' not found in {encoder_name} encoder.")
                print(f"Available options: {available_classes}")
                value = available_classes[0]  # Use first available option
                print(f"Using default: '{value}'")
        
        return encoder.transform([value])[0]
    
    def encode_weight_bin(self, weight):
        """Encode weight into bins matching the training data"""
        if weight < 0.5:
            return 0
        elif weight < 1.0:
            return 1
        elif weight < 2.0:
            return 2
        elif weight < 5.0:
            return 3
        else:
            return 4
    
    def predict_eco_score(self, product_data):
        """
        Predict eco score for a product using the most efficient method
        
        Args:
            product_data: Dict with keys: material, weight, transport, recyclability, origin
        
        Returns:
            Dict with prediction results
        """
        try:
            # Extract and validate input data
            material = product_data.get('material', 'Other')
            weight = float(product_data.get('weight', 0.5))
            transport = product_data.get('transport', 'Ship')
            recyclability = product_data.get('recyclability', 'Medium')
            origin = product_data.get('origin', 'China')
            
            # Encode features
            material_encoded = self.safe_encode(material, 'material', 'Other')
            transport_encoded = self.safe_encode(transport, 'transport', 'Ship')
            recyclability_encoded = self.safe_encode(recyclability, 'recyclability', 'Medium')
            origin_encoded = self.safe_encode(origin, 'origin', 'China')
            
            # Create engineered features to match the trained model
            weight_log = np.log1p(weight)  # log(1 + weight)
            weight_bin_encoded = self.encode_weight_bin(weight)
            
            # Create composite features
            material_transport_encoded = material_encoded * 10 + transport_encoded  # Composite feature
            origin_recycle_encoded = origin_encoded * 10 + recyclability_encoded  # Composite feature
            
            # Create feature vector matching the trained model exactly
            features = pd.DataFrame([{
                'material_encoded': material_encoded,
                'transport_encoded': transport_encoded,
                'recyclability_encoded': recyclability_encoded,
                'origin_encoded': origin_encoded,
                'weight_log': weight_log,
                'weight_bin_encoded': weight_bin_encoded,
                'material_transport_encoded': material_transport_encoded,
                'origin_recycle_encoded': origin_recycle_encoded
            }])
            
            # Create DMatrix for XGBoost
            dmat = xgb.DMatrix(features)
            
            # Make prediction
            prediction_probs = self.model.predict(dmat)
            predicted_class = np.argmax(prediction_probs, axis=1)[0]
            predicted_label = self.encoders['label'].inverse_transform([predicted_class])[0]
            confidence = float(np.max(prediction_probs[0])) * 100
            
            return {
                'eco_score': predicted_label,
                'confidence': round(confidence, 1),
                'carbon_footprint_kg': self.calculate_carbon_footprint(weight, transport, origin),
                'material_impact': self.calculate_material_impact(material, weight),
                'features_used': {
                    'material': material,
                    'weight': weight,
                    'transport': transport,
                    'recyclability': recyclability,
                    'origin': origin
                },
                'encoded_features': {
                    'material_encoded': int(material_encoded),
                    'transport_encoded': int(transport_encoded),
                    'recyclability_encoded': int(recyclability_encoded),
                    'origin_encoded': int(origin_encoded),
                    'weight_log': float(weight_log),
                    'weight_bin_encoded': int(weight_bin_encoded),
                    'material_transport_encoded': int(material_transport_encoded),
                    'origin_recycle_encoded': int(origin_recycle_encoded)
                }
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return {
                'eco_score': 'C',
                'confidence': 50.0,
                'carbon_footprint_kg': 1.0,
                'material_impact': 0.5,
                'error': str(e)
            }
    
    def calculate_carbon_footprint(self, weight, transport, origin):
        """Calculate carbon footprint based on weight, transport, and origin"""
        # Transport emission factors (kg CO2 per kg-km)
        transport_factors = {
            'Air': 0.5,
            'Ship': 0.03,
            'Truck': 0.15,
            'Land': 0.15
        }
        
        # Estimated distances from origin to UK (km)
        origin_distances = {
            'China': 8000,
            'USA': 6000,
            'Germany': 1000,
            'UK': 100,
            'India': 7000,
            'Brazil': 8500,
            'Other': 5000
        }
        
        emission_factor = transport_factors.get(transport, 0.1)
        distance = origin_distances.get(origin, 5000)
        
        carbon_kg = weight * emission_factor * (distance / 1000)
        return round(carbon_kg, 2)
    
    def calculate_material_impact(self, material, weight):
        """Calculate material impact score"""
        # Material impact factors (lower is better)
        material_factors = {
            'Plastic': 0.8,
            'Glass': 0.4,
            'Aluminum': 0.6,
            'Steel': 0.5,
            'Paper': 0.3,
            'Cardboard': 0.2,
            'Wood': 0.1,
            'Bamboo': 0.1,
            'Other': 0.5
        }
        
        factor = material_factors.get(material, 0.5)
        return round(weight * factor, 2)
    
    def get_available_options(self):
        """Get all available options for each feature"""
        return {
            'materials': list(self.encoders['material'].classes_),
            'transport_modes': list(self.encoders['transport'].classes_),
            'recyclability_levels': list(self.encoders['recyclability'].classes_),
            'origins': list(self.encoders['origin'].classes_)
        }

# Global instance for efficient reuse
_predictor = None

def get_predictor():
    """Get or create the global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = EfficientEcoPredictor()
    return _predictor

def predict_single_product(product_data):
    """
    Convenient function to predict a single product
    
    Args:
        product_data: Dict with product information
        
    Returns:
        Dict with prediction results
    """
    predictor = get_predictor()
    return predictor.predict_eco_score(product_data)

def load_model_and_encoders():
    """Load model and encoders (compatibility function)"""
    predictor = get_predictor()
    return predictor.model, predictor.encoders, None

if __name__ == "__main__":
    # Test the efficient predictor
    predictor = EfficientEcoPredictor()
    
    test_product = {
        'material': 'Plastic',
        'weight': 0.5,
        'transport': 'Air',
        'recyclability': 'Medium',
        'origin': 'China'
    }
    
    result = predictor.predict_eco_score(test_product)
    print(f"Test result: {result}")
    
    print("\nAvailable options:")
    options = predictor.get_available_options()
    for key, values in options.items():
        print(f"{key}: {values}")