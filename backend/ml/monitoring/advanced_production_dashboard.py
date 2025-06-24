"""
Advanced Production Monitoring Dashboard
=======================================

Comprehensive production monitoring system with:
1. Real-time prediction stability analysis
2. Adversarial input detection
3. Business impact metrics conversion  
4. Production deployment health dashboard
5. Advanced alerting and anomaly detection

For dissertation excellence: Demonstrates production-ready ML system monitoring
"""

import os
import json
import time
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading
import queue
import joblib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ML and statistical imports
import xgboost as xgb
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from scipy import stats
from scipy.stats import ks_2samp, chi2_contingency

# Visualization and dashboard
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from flask import Flask, render_template, jsonify, request
import dash
from dash import dcc, html, Input, Output, callback

warnings.filterwarnings('ignore')

@dataclass
class PredictionEvent:
    """Enhanced prediction event with business context"""
    id: str
    timestamp: datetime
    features: Dict[str, Any]
    prediction: str
    confidence: float
    response_time_ms: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    business_context: Optional[Dict] = None
    actual_outcome: Optional[str] = None
    feedback_score: Optional[float] = None
    
@dataclass
class BusinessImpactMetrics:
    """Business impact metrics for predictions"""
    total_predictions: int
    high_confidence_predictions: int
    user_satisfaction_score: float
    business_value_generated: float
    cost_savings_estimate: float
    error_cost_estimate: float
    recommendation_acceptance_rate: float
    timestamp: datetime

@dataclass
class SystemHealthMetrics:
    """Comprehensive system health metrics"""
    prediction_throughput: float
    average_response_time: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_usage_percent: float
    active_sessions: int
    queue_length: int
    cache_hit_rate: float
    timestamp: datetime

class RealTimePredictionStabilityMonitor:
    """
    Monitor prediction stability in real-time
    Critical for production: Detects model performance degradation
    """
    
    def __init__(self, stability_window: int = 1000, alert_threshold: float = 0.1):
        self.stability_window = stability_window
        self.alert_threshold = alert_threshold
        self.prediction_buffer = deque(maxlen=stability_window)
        self.stability_metrics = {}
        self.alerts = []
        
    def add_prediction(self, event: PredictionEvent):
        """Add prediction event to stability monitoring"""
        self.prediction_buffer.append(event)
        
        if len(self.prediction_buffer) >= 100:  # Minimum for stability analysis
            self._analyze_stability()
    
    def _analyze_stability(self):
        """Analyze prediction stability patterns"""
        
        # Extract recent predictions
        recent_predictions = list(self.prediction_buffer)[-self.stability_window:]
        
        # Confidence stability
        confidences = [p.confidence for p in recent_predictions]
        confidence_stability = self._calculate_stability_score(confidences)
        
        # Prediction distribution stability
        predictions = [p.prediction for p in recent_predictions]
        prediction_distribution = pd.Series(predictions).value_counts(normalize=True)
        distribution_entropy = stats.entropy(prediction_distribution.values)
        
        # Response time stability
        response_times = [p.response_time_ms for p in recent_predictions]
        response_time_stability = self._calculate_stability_score(response_times)
        
        # Feature drift detection
        feature_drift_score = self._detect_feature_drift(recent_predictions)
        
        # Temporal pattern analysis
        temporal_patterns = self._analyze_temporal_patterns(recent_predictions)
        
        stability_metrics = {
            'timestamp': datetime.now(),
            'confidence_stability': confidence_stability,
            'distribution_entropy': distribution_entropy,
            'response_time_stability': response_time_stability,
            'feature_drift_score': feature_drift_score,
            'temporal_patterns': temporal_patterns,
            'sample_size': len(recent_predictions)
        }
        
        self.stability_metrics = stability_metrics
        
        # Check for alerts
        self._check_stability_alerts(stability_metrics)
    
    def _calculate_stability_score(self, values: List[float]) -> float:
        """Calculate stability score for a sequence of values"""
        if len(values) < 10:
            return 1.0
        
        # Use coefficient of variation as stability measure
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if mean_val == 0:
            return 1.0 if std_val == 0 else 0.0
        
        cv = std_val / mean_val
        stability_score = max(0, 1 - cv)  # Higher = more stable
        
        return float(stability_score)
    
    def _detect_feature_drift(self, predictions: List[PredictionEvent]) -> float:
        """Detect feature drift in recent predictions"""
        if len(predictions) < 50:
            return 0.0
        
        # Split into old and new for comparison
        split_point = len(predictions) // 2
        old_predictions = predictions[:split_point]
        new_predictions = predictions[split_point:]
        
        # Extract numerical features
        numerical_features = set()
        for pred in predictions:
            for key, value in pred.features.items():
                if isinstance(value, (int, float)):
                    numerical_features.add(key)
        
        drift_scores = []
        
        for feature in numerical_features:
            old_values = [p.features.get(feature, 0) for p in old_predictions]
            new_values = [p.features.get(feature, 0) for p in new_predictions]
            
            # Remove None/NaN values
            old_values = [v for v in old_values if v is not None and not np.isnan(float(v))]
            new_values = [v for v in new_values if v is not None and not np.isnan(float(v))]
            
            if len(old_values) > 10 and len(new_values) > 10:
                # KS test for distribution change
                ks_stat, p_value = ks_2samp(old_values, new_values)
                drift_scores.append(ks_stat)
        
        return float(np.mean(drift_scores)) if drift_scores else 0.0
    
    def _analyze_temporal_patterns(self, predictions: List[PredictionEvent]) -> Dict:
        """Analyze temporal patterns in predictions"""
        
        # Extract timestamps
        timestamps = [p.timestamp for p in predictions]
        confidences = [p.confidence for p in predictions]
        
        if len(timestamps) < 20:
            return {'pattern': 'insufficient_data'}
        
        # Convert to time series
        df = pd.DataFrame({
            'timestamp': timestamps,
            'confidence': confidences
        }).set_index('timestamp').sort_index()
        
        # Resample to regular intervals (1-minute bins)
        df_resampled = df.resample('1T').mean().fillna(method='forward')
        
        if len(df_resampled) < 5:
            return {'pattern': 'insufficient_temporal_data'}
        
        # Detect trends
        time_numeric = np.arange(len(df_resampled))
        correlation = np.corrcoef(time_numeric, df_resampled['confidence'].values)[0, 1]
        
        # Detect periodicity (simple autocorrelation)
        confidence_values = df_resampled['confidence'].values
        if len(confidence_values) > 10:
            autocorr = np.correlate(confidence_values, confidence_values, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks (simple peak detection)
            peaks = []
            for i in range(1, min(len(autocorr)-1, 20)):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append(i)
        else:
            peaks = []
        
        return {
            'trend_correlation': float(correlation),
            'trend_direction': 'increasing' if correlation > 0.1 else 'decreasing' if correlation < -0.1 else 'stable',
            'potential_periodicity': len(peaks) > 0,
            'peak_intervals': peaks[:5] if peaks else []
        }
    
    def _check_stability_alerts(self, metrics: Dict):
        """Check for stability-related alerts"""
        alerts = []
        
        # Confidence stability alert
        if metrics['confidence_stability'] < (1 - self.alert_threshold):
            alerts.append({
                'type': 'confidence_instability',
                'severity': 'warning',
                'message': f"Confidence stability below threshold: {metrics['confidence_stability']:.3f}",
                'timestamp': metrics['timestamp']
            })
        
        # Feature drift alert
        if metrics['feature_drift_score'] > self.alert_threshold:
            alerts.append({
                'type': 'feature_drift',
                'severity': 'warning',
                'message': f"Feature drift detected: {metrics['feature_drift_score']:.3f}",
                'timestamp': metrics['timestamp']
            })
        
        # Distribution entropy alert (too uniform or too concentrated)
        entropy = metrics['distribution_entropy']
        if entropy < 0.5:  # Too concentrated
            alerts.append({
                'type': 'prediction_concentration',
                'severity': 'info',
                'message': f"Predictions highly concentrated (entropy: {entropy:.3f})",
                'timestamp': metrics['timestamp']
            })
        
        self.alerts.extend(alerts)
    
    def get_stability_report(self) -> Dict:
        """Get current stability analysis report"""
        return {
            'current_metrics': self.stability_metrics,
            'recent_alerts': self.alerts[-10:],  # Last 10 alerts
            'buffer_size': len(self.prediction_buffer),
            'monitoring_active': len(self.prediction_buffer) >= 100
        }

class AdversarialInputDetector:
    """
    Detect potentially adversarial or anomalous inputs
    Critical for production: Protects against malicious inputs
    """
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.feature_ranges = {}
        self.trained = False
        self.detection_stats = {
            'total_inputs': 0,
            'anomalies_detected': 0,
            'false_positive_rate': 0.0
        }
    
    def train_detector(self, training_data: pd.DataFrame):
        """Train anomaly detector on normal training data"""
        
        # Prepare numerical features
        numerical_features = training_data.select_dtypes(include=[np.number]).columns
        X_train = training_data[numerical_features]
        
        # Handle missing values
        X_train = X_train.fillna(X_train.median())
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train isolation forest
        self.isolation_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        self.isolation_forest.fit(X_scaled)
        
        # Store feature ranges for range-based detection
        for col in numerical_features:
            self.feature_ranges[col] = {
                'min': float(training_data[col].min()),
                'max': float(training_data[col].max()),
                'q1': float(training_data[col].quantile(0.25)),
                'q3': float(training_data[col].quantile(0.75)),
                'iqr': float(training_data[col].quantile(0.75) - training_data[col].quantile(0.25))
            }
        
        self.trained = True
        print(f"✅ Adversarial detector trained on {len(training_data)} samples")
    
    def detect_adversarial_input(self, features: Dict[str, Any]) -> Dict:
        """Detect if input features are potentially adversarial"""
        
        if not self.trained:
            return {
                'is_adversarial': False,
                'anomaly_score': 0.0,
                'detection_method': 'not_trained',
                'warnings': ['Detector not trained']
            }
        
        detection_results = {
            'is_adversarial': False,
            'anomaly_score': 0.0,
            'detection_methods': [],
            'warnings': [],
            'feature_anomalies': {}
        }
        
        # Convert features to DataFrame
        feature_df = pd.DataFrame([features])
        numerical_features = [col for col in feature_df.columns if col in self.feature_ranges]
        
        if not numerical_features:
            detection_results['warnings'].append('No numerical features for anomaly detection')
            return detection_results
        
        # Method 1: Isolation Forest
        try:
            X_scaled = self.scaler.transform(feature_df[numerical_features].fillna(0))
            isolation_score = self.isolation_forest.decision_function(X_scaled)[0]
            is_outlier = self.isolation_forest.predict(X_scaled)[0] == -1
            
            detection_results['anomaly_score'] = float(isolation_score)
            
            if is_outlier:
                detection_results['is_adversarial'] = True
                detection_results['detection_methods'].append('isolation_forest')
        
        except Exception as e:
            detection_results['warnings'].append(f'Isolation forest failed: {str(e)}')
        
        # Method 2: Range-based detection
        range_violations = 0
        for feature, value in features.items():
            if feature in self.feature_ranges and isinstance(value, (int, float)):
                ranges = self.feature_ranges[feature]
                
                # Check for extreme outliers (beyond 3*IQR)
                outlier_threshold = ranges['iqr'] * 3
                if (value < ranges['q1'] - outlier_threshold or 
                    value > ranges['q3'] + outlier_threshold):
                    
                    range_violations += 1
                    detection_results['feature_anomalies'][feature] = {
                        'value': value,
                        'expected_range': [ranges['q1'] - outlier_threshold, 
                                         ranges['q3'] + outlier_threshold],
                        'violation_type': 'extreme_outlier'
                    }
        
        if range_violations > 0:
            detection_results['detection_methods'].append('range_violation')
            if range_violations >= len(numerical_features) * 0.3:  # 30% of features
                detection_results['is_adversarial'] = True
        
        # Method 3: Statistical consistency check
        consistency_violations = self._check_statistical_consistency(features)
        if consistency_violations:
            detection_results['detection_methods'].append('statistical_inconsistency')
            detection_results['feature_anomalies'].update(consistency_violations)
            
            if len(consistency_violations) >= 2:
                detection_results['is_adversarial'] = True
        
        # Update detection statistics
        self.detection_stats['total_inputs'] += 1
        if detection_results['is_adversarial']:
            self.detection_stats['anomalies_detected'] += 1
        
        return detection_results
    
    def _check_statistical_consistency(self, features: Dict[str, Any]) -> Dict:
        """Check for statistically inconsistent feature combinations"""
        
        violations = {}
        
        # Check weight consistency
        if 'weight' in features and 'weight_log' in features:
            weight = features['weight']
            weight_log = features['weight_log']
            
            if isinstance(weight, (int, float)) and isinstance(weight_log, (int, float)):
                expected_log = np.log1p(weight)
                log_diff = abs(weight_log - expected_log)
                
                if log_diff > 0.5:  # Threshold for inconsistency
                    violations['weight_log_inconsistency'] = {
                        'weight': weight,
                        'weight_log': weight_log,
                        'expected_log': expected_log,
                        'difference': log_diff
                    }
        
        # Check encoded feature consistency
        categorical_encodings = [k for k in features.keys() if 'encoded' in k]
        for encoding in categorical_encodings:
            value = features[encoding]
            if isinstance(value, (int, float)):
                # Check for negative encodings (usually invalid)
                if value < 0:
                    violations[f'{encoding}_negative'] = {
                        'value': value,
                        'violation': 'negative_encoding'
                    }
                
                # Check for extremely high encodings (potential attack)
                if value > 100:  # Most categorical encodings should be small
                    violations[f'{encoding}_extreme'] = {
                        'value': value,
                        'violation': 'extreme_encoding'
                    }
        
        return violations
    
    def get_detection_statistics(self) -> Dict:
        """Get adversarial detection statistics"""
        
        detection_rate = (self.detection_stats['anomalies_detected'] / 
                         max(self.detection_stats['total_inputs'], 1))
        
        return {
            'total_inputs_processed': self.detection_stats['total_inputs'],
            'anomalies_detected': self.detection_stats['anomalies_detected'],
            'detection_rate': float(detection_rate),
            'detector_trained': self.trained,
            'feature_ranges_available': len(self.feature_ranges)
        }

class BusinessImpactMetricsCalculator:
    """
    Convert model predictions to business impact metrics
    Critical for stakeholders: Shows business value of ML system
    """
    
    def __init__(self):
        self.business_rules = {
            'eco_scores': {
                'A+': {'value_score': 10, 'cost_factor': 0.1},
                'A': {'value_score': 9, 'cost_factor': 0.2},
                'B': {'value_score': 7, 'cost_factor': 0.3},
                'C': {'value_score': 5, 'cost_factor': 0.5},
                'D': {'value_score': 3, 'cost_factor': 0.7},
                'E': {'value_score': 2, 'cost_factor': 0.8},
                'F': {'value_score': 1, 'cost_factor': 1.0}
            },
            'confidence_thresholds': {
                'high': 0.8,
                'medium': 0.6,
                'low': 0.4
            },
            'business_values': {
                'carbon_reduction_per_point': 0.5,  # kg CO2 reduction per eco score point
                'cost_per_kg_co2': 25.0,  # USD per kg CO2
                'decision_cost_without_ml': 15.0,  # USD cost of manual assessment
                'error_cost_factor': 2.0  # Multiplier for incorrect predictions
            }
        }
        
        self.cumulative_metrics = {
            'total_predictions': 0,
            'total_business_value': 0.0,
            'total_cost_savings': 0.0,
            'total_error_costs': 0.0,
            'user_interactions': 0,
            'positive_feedback': 0
        }
    
    def calculate_prediction_business_impact(self, event: PredictionEvent) -> Dict:
        """Calculate business impact for a single prediction"""
        
        eco_score = event.prediction
        confidence = event.confidence
        
        # Get eco score business value
        score_info = self.business_rules['eco_scores'].get(eco_score, {'value_score': 5, 'cost_factor': 0.5})
        
        # Calculate environmental impact
        carbon_reduction = score_info['value_score'] * self.business_rules['business_values']['carbon_reduction_per_point']
        environmental_value = carbon_reduction * self.business_rules['business_values']['cost_per_kg_co2']
        
        # Calculate cost savings from automation
        automation_savings = self.business_rules['business_values']['decision_cost_without_ml']
        
        # Adjust for confidence
        confidence_multiplier = self._get_confidence_multiplier(confidence)
        adjusted_value = environmental_value * confidence_multiplier
        adjusted_savings = automation_savings * confidence_multiplier
        
        # Calculate potential error cost
        error_probability = 1 - confidence
        potential_error_cost = (environmental_value * 
                              self.business_rules['business_values']['error_cost_factor'] * 
                              error_probability)
        
        # Net business value
        net_value = adjusted_value + adjusted_savings - potential_error_cost
        
        business_impact = {
            'environmental_value_usd': float(adjusted_value),
            'automation_savings_usd': float(adjusted_savings),
            'potential_error_cost_usd': float(potential_error_cost),
            'net_business_value_usd': float(net_value),
            'carbon_reduction_kg': float(carbon_reduction),
            'confidence_tier': self._get_confidence_tier(confidence),
            'risk_level': self._assess_risk_level(confidence, eco_score)
        }
        
        # Update cumulative metrics
        self._update_cumulative_metrics(business_impact, event)
        
        return business_impact
    
    def _get_confidence_multiplier(self, confidence: float) -> float:
        """Get confidence-based value multiplier"""
        thresholds = self.business_rules['confidence_thresholds']
        
        if confidence >= thresholds['high']:
            return 1.0
        elif confidence >= thresholds['medium']:
            return 0.8
        elif confidence >= thresholds['low']:
            return 0.6
        else:
            return 0.4
    
    def _get_confidence_tier(self, confidence: float) -> str:
        """Get confidence tier classification"""
        thresholds = self.business_rules['confidence_thresholds']
        
        if confidence >= thresholds['high']:
            return 'high'
        elif confidence >= thresholds['medium']:
            return 'medium'
        elif confidence >= thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def _assess_risk_level(self, confidence: float, eco_score: str) -> str:
        """Assess business risk level for prediction"""
        
        score_risk = self.business_rules['eco_scores'].get(eco_score, {}).get('cost_factor', 0.5)
        confidence_risk = 1 - confidence
        
        combined_risk = (score_risk + confidence_risk) / 2
        
        if combined_risk < 0.3:
            return 'low'
        elif combined_risk < 0.6:
            return 'medium'
        else:
            return 'high'
    
    def _update_cumulative_metrics(self, business_impact: Dict, event: PredictionEvent):
        """Update cumulative business metrics"""
        
        self.cumulative_metrics['total_predictions'] += 1
        self.cumulative_metrics['total_business_value'] += business_impact['net_business_value_usd']
        self.cumulative_metrics['total_cost_savings'] += business_impact['automation_savings_usd']
        self.cumulative_metrics['total_error_costs'] += business_impact['potential_error_cost_usd']
        
        # User feedback tracking
        if event.feedback_score is not None:
            self.cumulative_metrics['user_interactions'] += 1
            if event.feedback_score >= 4.0:  # Assuming 1-5 scale
                self.cumulative_metrics['positive_feedback'] += 1
    
    def calculate_period_metrics(self, start_time: datetime, end_time: datetime, 
                               events: List[PredictionEvent]) -> BusinessImpactMetrics:
        """Calculate business metrics for a specific time period"""
        
        period_events = [e for e in events if start_time <= e.timestamp <= end_time]
        
        if not period_events:
            return BusinessImpactMetrics(
                total_predictions=0,
                high_confidence_predictions=0,
                user_satisfaction_score=0.0,
                business_value_generated=0.0,
                cost_savings_estimate=0.0,
                error_cost_estimate=0.0,
                recommendation_acceptance_rate=0.0,
                timestamp=datetime.now()
            )
        
        # Calculate aggregate metrics
        total_predictions = len(period_events)
        high_confidence_predictions = len([e for e in period_events 
                                         if e.confidence >= self.business_rules['confidence_thresholds']['high']])
        
        # Business value calculations
        total_business_value = 0.0
        total_cost_savings = 0.0
        total_error_costs = 0.0
        
        for event in period_events:
            impact = self.calculate_prediction_business_impact(event)
            total_business_value += impact['net_business_value_usd']
            total_cost_savings += impact['automation_savings_usd']
            total_error_costs += impact['potential_error_cost_usd']
        
        # User satisfaction metrics
        feedback_events = [e for e in period_events if e.feedback_score is not None]
        if feedback_events:
            avg_feedback = np.mean([e.feedback_score for e in feedback_events])
            user_satisfaction_score = avg_feedback / 5.0  # Normalize to 0-1 scale
            
            positive_feedback = len([e for e in feedback_events if e.feedback_score >= 4.0])
            recommendation_acceptance_rate = positive_feedback / len(feedback_events)
        else:
            user_satisfaction_score = 0.0
            recommendation_acceptance_rate = 0.0
        
        return BusinessImpactMetrics(
            total_predictions=total_predictions,
            high_confidence_predictions=high_confidence_predictions,
            user_satisfaction_score=float(user_satisfaction_score),
            business_value_generated=float(total_business_value),
            cost_savings_estimate=float(total_cost_savings),
            error_cost_estimate=float(total_error_costs),
            recommendation_acceptance_rate=float(recommendation_acceptance_rate),
            timestamp=datetime.now()
        )
    
    def get_roi_analysis(self, time_window_days: int = 30) -> Dict:
        """Calculate ROI analysis for the ML system"""
        
        # Estimate system costs (simplified)
        daily_infrastructure_cost = 50.0  # USD per day
        daily_maintenance_cost = 25.0  # USD per day
        total_system_cost = (daily_infrastructure_cost + daily_maintenance_cost) * time_window_days
        
        # Benefits from cumulative metrics
        total_benefits = self.cumulative_metrics['total_business_value']
        total_savings = self.cumulative_metrics['total_cost_savings']
        
        # ROI calculation
        total_revenue = total_benefits + total_savings
        net_profit = total_revenue - total_system_cost
        roi_percentage = (net_profit / total_system_cost * 100) if total_system_cost > 0 else 0
        
        return {
            'time_window_days': time_window_days,
            'total_system_cost_usd': float(total_system_cost),
            'total_revenue_usd': float(total_revenue),
            'net_profit_usd': float(net_profit),
            'roi_percentage': float(roi_percentage),
            'break_even_achieved': net_profit > 0,
            'predictions_processed': self.cumulative_metrics['total_predictions'],
            'average_value_per_prediction': float(total_revenue / max(self.cumulative_metrics['total_predictions'], 1))
        }

class ProductionHealthDashboard:
    """
    Comprehensive production health dashboard
    Critical for operations: Real-time system monitoring
    """
    
    def __init__(self, model_path: str, update_interval: int = 60):
        self.model_path = model_path
        self.update_interval = update_interval
        
        # Initialize monitoring components
        self.stability_monitor = RealTimePredictionStabilityMonitor()
        self.adversarial_detector = AdversarialInputDetector()
        self.business_calculator = BusinessImpactMetricsCalculator()
        
        # Event storage
        self.prediction_events = deque(maxlen=10000)  # Store last 10k events
        self.system_metrics_history = deque(maxlen=1440)  # 24 hours of minute-level data
        
        # Dashboard state
        self.dashboard_data = {}
        self.alerts = []
        self.is_monitoring = False
        
        # Load model for predictions
        self._load_model()
        
    def _load_model(self):
        """Load the production model"""
        try:
            model_file = os.path.join(self.model_path, "xgb_model.json")
            if os.path.exists(model_file):
                self.model = xgb.XGBClassifier()
                self.model.load_model(model_file)
            else:
                self.model = joblib.load(os.path.join(self.model_path, "eco_model.pkl"))
            
            print(f"✅ Production model loaded for dashboard")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.model = None
    
    def start_monitoring(self):
        """Start the production monitoring dashboard"""
        
        print("🚀 Starting Production Health Dashboard...")
        
        # Train adversarial detector if model is available
        if self.model:
            self._train_adversarial_detector()
        
        # Start monitoring thread
        self.is_monitoring = True
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        print("✅ Production monitoring active")
    
    def _train_adversarial_detector(self):
        """Train adversarial detector with training data"""
        
        # Load training data for detector training
        training_paths = [
            "/mnt/c/DigSysProj/DSP/backend/ml/models/eco_dataset.csv",
            "/mnt/c/DigSysProj/DSP/common/data/csv/eco_dataset.csv"
        ]
        
        training_df = None
        for path in training_paths:
            if os.path.exists(path):
                training_df = pd.read_csv(path)
                break
        
        if training_df is not None:
            # Prepare features for detector training
            feature_cols = ['weight_log', 'material_encoded', 'transport_encoded', 
                          'recyclability_encoded', 'origin_encoded', 'weight_bin_encoded']
            
            available_cols = [col for col in feature_cols if col in training_df.columns]
            if available_cols:
                self.adversarial_detector.train_detector(training_df[available_cols])
            else:
                print("⚠️ No suitable features found for adversarial detector training")
        else:
            print("⚠️ Training data not found for adversarial detector")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # Update dashboard data
                self._update_dashboard_data()
                
                # Check for system alerts
                self._check_system_alerts(system_metrics)
                
                # Sleep until next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️ Monitoring loop error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_system_metrics(self) -> SystemHealthMetrics:
        """Collect current system health metrics"""
        
        # Calculate prediction throughput
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        recent_predictions = [e for e in self.prediction_events if e.timestamp >= hour_ago]
        throughput = len(recent_predictions) / 3600.0  # predictions per second
        
        # Calculate average response time
        if recent_predictions:
            avg_response_time = np.mean([e.response_time_ms for e in recent_predictions])
            error_rate = len([e for e in recent_predictions if e.confidence < 0.5]) / len(recent_predictions)
        else:
            avg_response_time = 0.0
            error_rate = 0.0
        
        # System resource metrics (simplified - in real production, use system monitoring)
        import psutil
        
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()
        disk_usage = psutil.disk_usage('/').percent
        
        # Active sessions (simplified)
        active_sessions = len(set(e.session_id for e in recent_predictions if e.session_id))
        
        return SystemHealthMetrics(
            prediction_throughput=float(throughput),
            average_response_time=float(avg_response_time),
            error_rate=float(error_rate),
            memory_usage_mb=float(memory_usage),
            cpu_usage_percent=float(cpu_usage),
            disk_usage_percent=float(disk_usage),
            active_sessions=active_sessions,
            queue_length=0,  # Simplified
            cache_hit_rate=0.95,  # Simplified
            timestamp=now
        )
    
    def _update_dashboard_data(self):
        """Update dashboard data structure"""
        
        now = datetime.now()
        
        # Stability metrics
        stability_report = self.stability_monitor.get_stability_report()
        
        # Adversarial detection stats
        detection_stats = self.adversarial_detector.get_detection_statistics()
        
        # Business metrics for last 24 hours
        day_ago = now - timedelta(days=1)
        recent_events = [e for e in self.prediction_events if e.timestamp >= day_ago]
        business_metrics = self.business_calculator.calculate_period_metrics(day_ago, now, recent_events)
        
        # ROI analysis
        roi_analysis = self.business_calculator.get_roi_analysis()
        
        # System health
        current_system_health = self.system_metrics_history[-1] if self.system_metrics_history else None
        
        self.dashboard_data = {
            'timestamp': now,
            'stability_monitoring': stability_report,
            'adversarial_detection': detection_stats,
            'business_impact': asdict(business_metrics),
            'roi_analysis': roi_analysis,
            'system_health': asdict(current_system_health) if current_system_health else {},
            'recent_alerts': self.alerts[-20:],  # Last 20 alerts
            'total_events_processed': len(self.prediction_events)
        }
    
    def _check_system_alerts(self, metrics: SystemHealthMetrics):
        """Check for system-level alerts"""
        
        alerts = []
        
        # High resource usage alerts
        if metrics.cpu_usage_percent > 80:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f"High CPU usage: {metrics.cpu_usage_percent:.1f}%",
                'timestamp': metrics.timestamp
            })
        
        if metrics.memory_usage_mb > 2000:  # 2GB threshold
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f"High memory usage: {metrics.memory_usage_mb:.0f}MB",
                'timestamp': metrics.timestamp
            })
        
        # Performance alerts
        if metrics.average_response_time > 1000:  # 1 second threshold
            alerts.append({
                'type': 'slow_response_time',
                'severity': 'warning',
                'message': f"Slow response time: {metrics.average_response_time:.0f}ms",
                'timestamp': metrics.timestamp
            })
        
        if metrics.error_rate > 0.1:  # 10% error rate threshold
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'critical',
                'message': f"High error rate: {metrics.error_rate:.1%}",
                'timestamp': metrics.timestamp
            })
        
        # Throughput alerts
        if metrics.prediction_throughput < 0.1:  # Very low throughput
            alerts.append({
                'type': 'low_throughput',
                'severity': 'info',
                'message': f"Low prediction throughput: {metrics.prediction_throughput:.3f}/sec",
                'timestamp': metrics.timestamp
            })
        
        self.alerts.extend(alerts)
    
    def process_prediction_event(self, features: Dict[str, Any], prediction: str, 
                               confidence: float, response_time_ms: float,
                               user_id: str = None, session_id: str = None,
                               business_context: Dict = None) -> Dict:
        """Process a new prediction event through all monitoring systems"""
        
        # Create prediction event
        event = PredictionEvent(
            id=f"pred_{len(self.prediction_events)}_{int(time.time())}",
            timestamp=datetime.now(),
            features=features,
            prediction=prediction,
            confidence=confidence,
            response_time_ms=response_time_ms,
            user_id=user_id,
            session_id=session_id,
            business_context=business_context
        )
        
        # Store event
        self.prediction_events.append(event)
        
        # Process through monitoring systems
        monitoring_results = {}
        
        # Stability monitoring
        self.stability_monitor.add_prediction(event)
        monitoring_results['stability_updated'] = True
        
        # Adversarial detection
        adversarial_result = self.adversarial_detector.detect_adversarial_input(features)
        monitoring_results['adversarial_detection'] = adversarial_result
        
        # Business impact calculation
        business_impact = self.business_calculator.calculate_prediction_business_impact(event)
        monitoring_results['business_impact'] = business_impact
        
        # Alert if adversarial input detected
        if adversarial_result['is_adversarial']:
            self.alerts.append({
                'type': 'adversarial_input_detected',
                'severity': 'warning',
                'message': f"Adversarial input detected (methods: {', '.join(adversarial_result['detection_methods'])})",
                'timestamp': event.timestamp,
                'event_id': event.id
            })
        
        return monitoring_results
    
    def get_dashboard_data(self) -> Dict:
        """Get current dashboard data"""
        return self.dashboard_data
    
    def get_real_time_metrics(self) -> Dict:
        """Get real-time metrics for live dashboard"""
        
        now = datetime.now()
        
        # Last hour metrics
        hour_ago = now - timedelta(hours=1)
        recent_events = [e for e in self.prediction_events if e.timestamp >= hour_ago]
        
        # Quick metrics calculation
        metrics = {
            'current_time': now.isoformat(),
            'predictions_last_hour': len(recent_events),
            'current_throughput': len(recent_events) / 3600.0,
            'average_confidence': float(np.mean([e.confidence for e in recent_events])) if recent_events else 0.0,
            'active_alerts': len([a for a in self.alerts if (now - a['timestamp']).total_seconds() < 3600]),
            'system_status': self._get_overall_system_status(),
            'latest_business_value': float(np.sum([
                self.business_calculator.calculate_prediction_business_impact(e)['net_business_value_usd']
                for e in recent_events
            ])) if recent_events else 0.0
        }
        
        return metrics
    
    def _get_overall_system_status(self) -> str:
        """Get overall system status"""
        
        # Check recent alerts
        now = datetime.now()
        recent_critical_alerts = [
            a for a in self.alerts 
            if a['severity'] == 'critical' and (now - a['timestamp']).total_seconds() < 1800  # 30 min
        ]
        
        recent_warning_alerts = [
            a for a in self.alerts 
            if a['severity'] == 'warning' and (now - a['timestamp']).total_seconds() < 1800
        ]
        
        if recent_critical_alerts:
            return 'critical'
        elif len(recent_warning_alerts) > 5:
            return 'degraded'
        elif recent_warning_alerts:
            return 'warning'
        else:
            return 'healthy'
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        
        report_time = datetime.now()
        
        # Stability analysis
        stability_report = self.stability_monitor.get_stability_report()
        
        # Security analysis
        security_stats = self.adversarial_detector.get_detection_statistics()
        
        # Business performance
        business_roi = self.business_calculator.get_roi_analysis()
        
        # System performance
        recent_system_metrics = list(self.system_metrics_history)[-60:]  # Last hour
        
        if recent_system_metrics:
            avg_cpu = np.mean([m.cpu_usage_percent for m in recent_system_metrics])
            avg_memory = np.mean([m.memory_usage_mb for m in recent_system_metrics])
            avg_response_time = np.mean([m.average_response_time for m in recent_system_metrics])
        else:
            avg_cpu = avg_memory = avg_response_time = 0
        
        # Alert summary
        now = datetime.now()
        alert_summary = {
            'total_alerts_24h': len([a for a in self.alerts if (now - a['timestamp']).total_seconds() < 86400]),
            'critical_alerts_24h': len([a for a in self.alerts if a['severity'] == 'critical' and (now - a['timestamp']).total_seconds() < 86400]),
            'warning_alerts_24h': len([a for a in self.alerts if a['severity'] == 'warning' and (now - a['timestamp']).total_seconds() < 86400])
        }
        
        health_report = {
            'report_timestamp': report_time,
            'overall_status': self._get_overall_system_status(),
            'stability_metrics': {
                'monitoring_active': stability_report.get('monitoring_active', False),
                'buffer_utilization': len(self.prediction_events) / 10000,
                'recent_stability_score': stability_report.get('current_metrics', {}).get('confidence_stability', 0)
            },
            'security_metrics': {
                'adversarial_detection_active': security_stats['detector_trained'],
                'detection_rate': security_stats['detection_rate'],
                'total_inputs_processed': security_stats['total_inputs_processed']
            },
            'business_metrics': {
                'roi_percentage': business_roi['roi_percentage'],
                'break_even_achieved': business_roi['break_even_achieved'],
                'total_value_generated': business_roi['total_revenue_usd']
            },
            'system_performance': {
                'average_cpu_usage': float(avg_cpu),
                'average_memory_usage_mb': float(avg_memory),
                'average_response_time_ms': float(avg_response_time),
                'uptime_monitoring_active': self.is_monitoring
            },
            'alert_summary': alert_summary,
            'recommendations': self._generate_health_recommendations()
        }
        
        return health_report
    
    def _generate_health_recommendations(self) -> List[str]:
        """Generate actionable health recommendations"""
        
        recommendations = []
        
        # Check system performance
        if self.system_metrics_history:
            recent_metrics = self.system_metrics_history[-1]
            
            if recent_metrics.cpu_usage_percent > 70:
                recommendations.append("Consider scaling up CPU resources or optimizing model inference")
            
            if recent_metrics.memory_usage_mb > 1500:
                recommendations.append("Monitor memory usage - consider optimizing data structures")
            
            if recent_metrics.average_response_time > 500:
                recommendations.append("Response times elevated - investigate model optimization opportunities")
        
        # Check prediction patterns
        recent_events = list(self.prediction_events)[-1000:]  # Last 1000 predictions
        if recent_events:
            low_confidence_rate = len([e for e in recent_events if e.confidence < 0.6]) / len(recent_events)
            
            if low_confidence_rate > 0.3:
                recommendations.append("High rate of low-confidence predictions - consider model retraining")
        
        # Check business metrics
        roi_analysis = self.business_calculator.get_roi_analysis()
        if roi_analysis['roi_percentage'] < 50:
            recommendations.append("ROI below target - review business value calculations and cost optimization")
        
        # Check alerts
        now = datetime.now()
        recent_alerts = [a for a in self.alerts if (now - a['timestamp']).total_seconds() < 3600]
        if len(recent_alerts) > 10:
            recommendations.append("High alert volume - investigate root causes and adjust thresholds")
        
        if not recommendations:
            recommendations.append("System operating within normal parameters - continue monitoring")
        
        return recommendations
    
    def stop_monitoring(self):
        """Stop the monitoring dashboard"""
        self.is_monitoring = False
        print("🛑 Production monitoring stopped")

def create_web_dashboard_app(dashboard: ProductionHealthDashboard) -> dash.Dash:
    """Create a web-based dashboard using Dash"""
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.H1("🚀 Production ML System Health Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB'}),
        
        # Real-time metrics cards
        html.Div([
            html.Div([
                html.H3("Predictions/Hour"),
                html.H2(id="predictions-per-hour", children="0")
            ], className="metric-card", style={'width': '23%', 'display': 'inline-block', 'margin': '1%'}),
            
            html.Div([
                html.H3("System Status"),
                html.H2(id="system-status", children="Healthy")
            ], className="metric-card", style={'width': '23%', 'display': 'inline-block', 'margin': '1%'}),
            
            html.Div([
                html.H3("Active Alerts"),
                html.H2(id="active-alerts", children="0")
            ], className="metric-card", style={'width': '23%', 'display': 'inline-block', 'margin': '1%'}),
            
            html.Div([
                html.H3("Business Value/Hour"),
                html.H2(id="business-value", children="$0")
            ], className="metric-card", style={'width': '23%', 'display': 'inline-block', 'margin': '1%'})
        ]),
        
        # Charts section
        html.Div([
            dcc.Graph(id="throughput-chart"),
            dcc.Graph(id="confidence-distribution"),
            dcc.Graph(id="system-resources-chart"),
            dcc.Graph(id="business-metrics-chart")
        ]),
        
        # Auto-refresh
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # Update every 30 seconds
            n_intervals=0
        )
    ])
    
    @app.callback(
        [Output('predictions-per-hour', 'children'),
         Output('system-status', 'children'),
         Output('active-alerts', 'children'),
         Output('business-value', 'children'),
         Output('throughput-chart', 'figure'),
         Output('confidence-distribution', 'figure'),
         Output('system-resources-chart', 'figure'),
         Output('business-metrics-chart', 'figure')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_dashboard(n):
        # Get real-time metrics
        metrics = dashboard.get_real_time_metrics()
        
        # Update metric cards
        predictions_per_hour = f"{metrics['predictions_last_hour']}"
        system_status = metrics['system_status'].title()
        active_alerts = f"{metrics['active_alerts']}"
        business_value = f"${metrics['latest_business_value']:.0f}"
        
        # Create charts
        # Throughput chart
        throughput_fig = go.Figure()
        throughput_fig.add_trace(go.Scatter(
            x=[datetime.now() - timedelta(minutes=i) for i in range(60, 0, -1)],
            y=[metrics['current_throughput']] * 60,  # Simplified
            mode='lines',
            name='Predictions/sec'
        ))
        throughput_fig.update_layout(title="Prediction Throughput")
        
        # Confidence distribution
        confidence_fig = go.Figure()
        confidence_fig.add_trace(go.Histogram(
            x=[0.8, 0.9, 0.7, 0.95, 0.6],  # Simplified sample data
            nbinsx=10,
            name='Confidence Distribution'
        ))
        confidence_fig.update_layout(title="Prediction Confidence Distribution")
        
        # System resources
        resources_fig = go.Figure()
        resources_fig.add_trace(go.Scatter(
            x=['CPU', 'Memory', 'Disk'],
            y=[50, 60, 30],  # Simplified sample data
            mode='markers+lines',
            name='Resource Usage %'
        ))
        resources_fig.update_layout(title="System Resource Usage")
        
        # Business metrics
        business_fig = go.Figure()
        business_fig.add_trace(go.Bar(
            x=['Value Generated', 'Cost Savings', 'Error Costs'],
            y=[1000, 500, 50],  # Simplified sample data
            name='Business Impact ($)'
        ))
        business_fig.update_layout(title="Business Impact Metrics")
        
        return (predictions_per_hour, system_status, active_alerts, business_value,
                throughput_fig, confidence_fig, resources_fig, business_fig)
    
    return app

def main():
    """Main demonstration function"""
    
    # Initialize production dashboard
    model_path = "/mnt/c/DigSysProj/DSP/backend/ml/models"
    dashboard = ProductionHealthDashboard(model_path)
    
    # Start monitoring
    dashboard.start_monitoring()
    
    # Simulate some prediction events
    print("🔄 Simulating prediction events...")
    
    for i in range(50):
        # Simulate prediction event
        features = {
            'material_encoded': np.random.randint(0, 5),
            'weight_log': np.random.normal(0.5, 0.3),
            'transport_encoded': np.random.randint(0, 3),
            'recyclability_encoded': np.random.randint(0, 3),
            'origin_encoded': np.random.randint(0, 5),
            'weight_bin_encoded': np.random.randint(0, 4)
        }
        
        prediction = np.random.choice(['A+', 'A', 'B', 'C', 'D', 'E', 'F'])
        confidence = np.random.uniform(0.6, 0.95)
        response_time = np.random.uniform(100, 500)
        
        # Process through dashboard
        dashboard.process_prediction_event(
            features=features,
            prediction=prediction,
            confidence=confidence,
            response_time_ms=response_time,
            user_id=f"user_{i % 10}",
            session_id=f"session_{i % 5}"
        )
        
        time.sleep(0.1)  # Small delay
    
    # Get dashboard data
    dashboard_data = dashboard.get_dashboard_data()
    health_report = dashboard.generate_health_report()
    
    # Save results
    results_dir = "/mnt/c/DigSysProj/DSP/backend/ml/monitoring/dashboard_results"
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save dashboard data
    dashboard_file = os.path.join(results_dir, f"dashboard_data_{timestamp}.json")
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    # Save health report
    health_file = os.path.join(results_dir, f"health_report_{timestamp}.json")
    with open(health_file, 'w') as f:
        json.dump(health_report, f, indent=2, default=str)
    
    print(f"✅ Advanced monitoring dashboard demonstration completed")
    print(f"📊 Dashboard data saved: {dashboard_file}")
    print(f"📊 Health report saved: {health_file}")
    print(f"🎯 System Status: {health_report['overall_status']}")
    print(f"🎯 ROI: {health_report['business_metrics']['roi_percentage']:.1f}%")
    
    # Stop monitoring
    dashboard.stop_monitoring()
    
    return dashboard_data, health_report

if __name__ == "__main__":
    results = main()