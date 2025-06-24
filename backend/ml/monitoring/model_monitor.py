"""
Model Monitoring and Deployment Readiness Framework
===================================================

Production-grade model monitoring system for dissertation:
1. Real-time model performance tracking
2. Prediction confidence monitoring
3. Model drift detection
4. Automated alerts and health checks
5. A/B testing framework preparation

For dissertation defense: Shows production deployment readiness and monitoring capabilities
"""

import os
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import warnings
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

# Statistical imports
from scipy import stats
from scipy.stats import ks_2samp, chi2_contingency
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictionRecord:
    """Individual prediction record for monitoring"""
    prediction: str
    confidence: float
    features: Dict[str, Any]
    timestamp: datetime
    actual_result: Optional[str] = None
    user_feedback: Optional[float] = None  # 1-5 rating
    response_time_ms: float = 0.0
    model_version: str = "1.0.0"
    
@dataclass
class ModelHealthMetrics:
    """Comprehensive model health assessment"""
    prediction_accuracy: float
    average_confidence: float
    response_time_p95: float
    error_rate: float
    predictions_per_hour: float
    confidence_drift_score: float
    feature_drift_detected: bool
    overall_health_score: float
    status: str  # "healthy", "warning", "critical"
    issues: List[str]
    timestamp: datetime

class ModelPerformanceMonitor:
    """
    Real-time model performance monitoring system
    """
    
    def __init__(self, window_size: int = 1000, alert_thresholds: Dict = None):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.feature_history = deque(maxlen=window_size)
        self.performance_history = []
        
        # Alert thresholds
        self.thresholds = alert_thresholds or {
            'min_confidence': 0.6,
            'max_response_time_ms': 2000,
            'max_error_rate': 0.05,
            'min_accuracy': 0.75,
            'confidence_drift_threshold': 0.1
        }
        
        # Thread-safe monitoring state
        self.lock = threading.Lock()
        self.monitoring_active = False
        
        # Baseline statistics (computed from training data)
        self.baseline_stats = None
        
        logger.info(f"Model monitor initialized with window size {window_size}")
    
    def log_prediction(self, prediction: str, confidence: float, 
                      features: Dict[str, Any], response_time_ms: float = 0.0,
                      actual_result: str = None, user_feedback: float = None) -> None:
        """
        Log a prediction for monitoring
        """
        with self.lock:
            record = PredictionRecord(
                prediction=prediction,
                confidence=confidence,
                features=features,
                timestamp=datetime.now(),
                actual_result=actual_result,
                user_feedback=user_feedback,
                response_time_ms=response_time_ms
            )
            
            self.predictions.append(record)
            self.feature_history.append(features)
            
            # Trigger monitoring checks if we have enough data
            if len(self.predictions) >= 10:
                self._check_real_time_health()
    
    def set_baseline_statistics(self, training_features: pd.DataFrame) -> None:
        """
        Set baseline statistics from training data for drift detection
        """
        self.baseline_stats = {}
        
        for column in training_features.columns:
            if training_features[column].dtype in ['int64', 'float64']:
                self.baseline_stats[column] = {
                    'mean': float(training_features[column].mean()),
                    'std': float(training_features[column].std()),
                    'quantiles': {
                        'q25': float(training_features[column].quantile(0.25)),
                        'q50': float(training_features[column].quantile(0.50)),
                        'q75': float(training_features[column].quantile(0.75))
                    }
                }
            else:
                # Categorical features
                value_counts = training_features[column].value_counts()
                self.baseline_stats[column] = {
                    'categories': value_counts.index.tolist(),
                    'proportions': (value_counts / len(training_features)).to_dict()
                }
        
        logger.info(f"Baseline statistics set for {len(self.baseline_stats)} features")
    
    def _check_real_time_health(self) -> None:
        """
        Perform real-time health checks on recent predictions
        """
        if len(self.predictions) < 10:
            return
        
        recent_predictions = list(self.predictions)[-50:]  # Last 50 predictions
        
        # Check confidence drift
        recent_confidences = [p.confidence for p in recent_predictions]
        avg_confidence = np.mean(recent_confidences)
        
        if avg_confidence < self.thresholds['min_confidence']:
            logger.warning(f"Low confidence detected: {avg_confidence:.3f}")
        
        # Check response time
        recent_response_times = [p.response_time_ms for p in recent_predictions if p.response_time_ms > 0]
        if recent_response_times:
            p95_response_time = np.percentile(recent_response_times, 95)
            if p95_response_time > self.thresholds['max_response_time_ms']:
                logger.warning(f"High response time detected: {p95_response_time:.1f}ms")
    
    def detect_feature_drift(self, significance_level: float = 0.05) -> Dict[str, Any]:
        """
        Detect feature drift compared to baseline statistics
        """
        if not self.baseline_stats or len(self.feature_history) < 30:
            return {'drift_detected': False, 'reason': 'Insufficient data'}
        
        drift_results = {}
        drift_detected = False
        
        # Convert recent features to DataFrame
        recent_features = pd.DataFrame(list(self.feature_history))
        
        for feature_name, baseline_info in self.baseline_stats.items():
            if feature_name not in recent_features.columns:
                continue
            
            recent_values = recent_features[feature_name].dropna()
            if len(recent_values) == 0:
                continue
            
            if 'mean' in baseline_info:  # Numerical feature
                try:
                    # Use synthetic baseline data for KS test
                    baseline_samples = np.random.normal(
                        baseline_info['mean'], 
                        baseline_info['std'], 
                        size=len(recent_values)
                    )
                    
                    ks_stat, p_value = ks_2samp(baseline_samples, recent_values)
                    
                    drift_results[feature_name] = {
                        'type': 'numerical',
                        'ks_statistic': float(ks_stat),
                        'p_value': float(p_value),
                        'drift_detected': p_value < significance_level,
                        'baseline_mean': baseline_info['mean'],
                        'current_mean': float(recent_values.mean()),
                        'mean_shift': float(recent_values.mean() - baseline_info['mean'])
                    }
                    
                    if p_value < significance_level:
                        drift_detected = True
                        
                except Exception as e:
                    logger.warning(f"Failed to test drift for {feature_name}: {e}")
            
            else:  # Categorical feature
                try:
                    current_proportions = recent_values.value_counts(normalize=True).to_dict()
                    baseline_proportions = baseline_info['proportions']
                    
                    # Simple proportion difference test
                    max_proportion_change = 0
                    for category in set(list(current_proportions.keys()) + list(baseline_proportions.keys())):
                        current_prop = current_proportions.get(category, 0)
                        baseline_prop = baseline_proportions.get(category, 0)
                        proportion_change = abs(current_prop - baseline_prop)
                        max_proportion_change = max(max_proportion_change, proportion_change)
                    
                    drift_results[feature_name] = {
                        'type': 'categorical',
                        'max_proportion_change': float(max_proportion_change),
                        'drift_detected': max_proportion_change > 0.2,  # 20% threshold
                        'baseline_categories': len(baseline_proportions),
                        'current_categories': len(current_proportions)
                    }
                    
                    if max_proportion_change > 0.2:
                        drift_detected = True
                        
                except Exception as e:
                    logger.warning(f"Failed to test categorical drift for {feature_name}: {e}")
        
        return {
            'drift_detected': drift_detected,
            'features_with_drift': sum(1 for r in drift_results.values() if r.get('drift_detected', False)),
            'total_features_tested': len(drift_results),
            'individual_results': drift_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_model_health(self) -> ModelHealthMetrics:
        """
        Calculate comprehensive model health metrics
        """
        if len(self.predictions) == 0:
            return ModelHealthMetrics(
                prediction_accuracy=0.0,
                average_confidence=0.0,
                response_time_p95=0.0,
                error_rate=1.0,
                predictions_per_hour=0.0,
                confidence_drift_score=0.0,
                feature_drift_detected=False,
                overall_health_score=0.0,
                status="no_data",
                issues=["No prediction data available"],
                timestamp=datetime.now()
            )
        
        predictions_list = list(self.predictions)
        issues = []
        
        # 1. Prediction Accuracy (if actual results available)
        predictions_with_actuals = [p for p in predictions_list if p.actual_result is not None]
        if predictions_with_actuals:
            y_true = [p.actual_result for p in predictions_with_actuals]
            y_pred = [p.prediction for p in predictions_with_actuals]
            accuracy = accuracy_score(y_true, y_pred)
        else:
            accuracy = 0.0  # Unknown without ground truth
        
        # 2. Average Confidence
        confidences = [p.confidence for p in predictions_list]
        avg_confidence = np.mean(confidences)
        
        if avg_confidence < self.thresholds['min_confidence']:
            issues.append(f"Low average confidence: {avg_confidence:.3f}")
        
        # 3. Response Time P95
        response_times = [p.response_time_ms for p in predictions_list if p.response_time_ms > 0]
        p95_response_time = np.percentile(response_times, 95) if response_times else 0
        
        if p95_response_time > self.thresholds['max_response_time_ms']:
            issues.append(f"High response time: {p95_response_time:.1f}ms")
        
        # 4. Error Rate (predictions with very low confidence)
        low_confidence_predictions = sum(1 for c in confidences if c < 0.3)
        error_rate = low_confidence_predictions / len(predictions_list)
        
        if error_rate > self.thresholds['max_error_rate']:
            issues.append(f"High error rate: {error_rate:.3f}")
        
        # 5. Predictions per Hour
        if len(predictions_list) > 1:
            time_span = (predictions_list[-1].timestamp - predictions_list[0].timestamp).total_seconds() / 3600
            predictions_per_hour = len(predictions_list) / max(time_span, 0.01)  # Avoid division by zero
        else:
            predictions_per_hour = 0
        
        # 6. Confidence Drift
        if len(confidences) >= 20:
            # Compare recent vs older confidences
            recent_confidences = confidences[-10:]
            older_confidences = confidences[:10]
            confidence_drift = abs(np.mean(recent_confidences) - np.mean(older_confidences))
        else:
            confidence_drift = 0
        
        if confidence_drift > self.thresholds['confidence_drift_threshold']:
            issues.append(f"Confidence drift detected: {confidence_drift:.3f}")
        
        # 7. Feature Drift
        drift_results = self.detect_feature_drift()
        feature_drift_detected = drift_results.get('drift_detected', False)
        
        if feature_drift_detected:
            issues.append(f"Feature drift detected in {drift_results.get('features_with_drift', 0)} features")
        
        # 8. Overall Health Score (weighted combination)
        health_components = {
            'accuracy': accuracy if predictions_with_actuals else 0.8,  # Assume decent accuracy if unknown
            'confidence': min(avg_confidence / 0.9, 1.0),  # Normalize to 0.9 as perfect
            'response_time': max(0, 1 - (p95_response_time / self.thresholds['max_response_time_ms'])),
            'error_rate': max(0, 1 - (error_rate / self.thresholds['max_error_rate'])),
            'confidence_stability': max(0, 1 - (confidence_drift / self.thresholds['confidence_drift_threshold']))
        }
        
        weights = {
            'accuracy': 0.3,
            'confidence': 0.25,
            'response_time': 0.2,
            'error_rate': 0.15,
            'confidence_stability': 0.1
        }
        
        overall_health_score = sum(
            health_components[metric] * weights[metric] 
            for metric in health_components
        )
        
        # 9. Status Determination
        if overall_health_score >= 0.8:
            status = "healthy"
        elif overall_health_score >= 0.6:
            status = "warning"
        else:
            status = "critical"
        
        return ModelHealthMetrics(
            prediction_accuracy=accuracy,
            average_confidence=avg_confidence,
            response_time_p95=p95_response_time,
            error_rate=error_rate,
            predictions_per_hour=predictions_per_hour,
            confidence_drift_score=confidence_drift,
            feature_drift_detected=feature_drift_detected,
            overall_health_score=overall_health_score,
            status=status,
            issues=issues,
            timestamp=datetime.now()
        )
    
    def get_performance_trends(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Get performance trends over specified time period
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_predictions = [p for p in self.predictions if p.timestamp >= cutoff_time]
        
        if not recent_predictions:
            return {'error': 'No data in specified time range'}
        
        # Group by hour
        hourly_stats = defaultdict(list)
        for pred in recent_predictions:
            hour_key = pred.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_stats[hour_key].append(pred)
        
        trends = {
            'hourly_confidence': {},
            'hourly_response_time': {},
            'hourly_prediction_count': {},
            'confidence_trend': 'stable',
            'response_time_trend': 'stable'
        }
        
        for hour, predictions in hourly_stats.items():
            hour_str = hour.isoformat()
            
            confidences = [p.confidence for p in predictions]
            response_times = [p.response_time_ms for p in predictions if p.response_time_ms > 0]
            
            trends['hourly_confidence'][hour_str] = np.mean(confidences)
            trends['hourly_response_time'][hour_str] = np.mean(response_times) if response_times else 0
            trends['hourly_prediction_count'][hour_str] = len(predictions)
        
        # Determine trends
        confidence_values = list(trends['hourly_confidence'].values())
        if len(confidence_values) >= 3:
            if confidence_values[-1] < confidence_values[0] - 0.05:
                trends['confidence_trend'] = 'declining'
            elif confidence_values[-1] > confidence_values[0] + 0.05:
                trends['confidence_trend'] = 'improving'
        
        response_time_values = list(trends['hourly_response_time'].values())
        if len(response_time_values) >= 3:
            avg_early = np.mean(response_time_values[:len(response_time_values)//2])
            avg_late = np.mean(response_time_values[len(response_time_values)//2:])
            if avg_late > avg_early * 1.2:
                trends['response_time_trend'] = 'degrading'
            elif avg_late < avg_early * 0.8:
                trends['response_time_trend'] = 'improving'
        
        return trends

class ModelDeploymentMonitor:
    """
    Production deployment monitoring and alerting system
    """
    
    def __init__(self, alert_callback=None):
        self.performance_monitor = ModelPerformanceMonitor()
        self.alert_callback = alert_callback or self._default_alert_handler
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Deployment metrics
        self.deployment_stats = {
            'deployment_time': datetime.now(),
            'total_predictions': 0,
            'uptime_seconds': 0,
            'error_count': 0,
            'alert_count': 0
        }
    
    def start_monitoring(self, check_interval_seconds: int = 300) -> None:
        """
        Start continuous monitoring in background thread
        """
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("Monitoring already active")
            return
        
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info(f"Model monitoring started with {check_interval_seconds}s intervals")
    
    def stop_monitoring_service(self) -> None:
        """
        Stop the monitoring service
        """
        self.stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        logger.info("Model monitoring stopped")
    
    def _monitoring_loop(self, check_interval: int) -> None:
        """
        Main monitoring loop
        """
        while not self.stop_monitoring.wait(check_interval):
            try:
                health_metrics = self.performance_monitor.calculate_model_health()
                
                # Update deployment stats
                self.deployment_stats['uptime_seconds'] = (
                    datetime.now() - self.deployment_stats['deployment_time']
                ).total_seconds()
                
                # Check for alerts
                if health_metrics.status in ['warning', 'critical']:
                    self._trigger_alert(health_metrics)
                
                # Log health status
                logger.info(f"Model health: {health_metrics.status} (score: {health_metrics.overall_health_score:.3f})")
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                self.deployment_stats['error_count'] += 1
    
    def _trigger_alert(self, health_metrics: ModelHealthMetrics) -> None:
        """
        Trigger alert based on health metrics
        """
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'severity': health_metrics.status,
            'health_score': health_metrics.overall_health_score,
            'issues': health_metrics.issues,
            'metrics': asdict(health_metrics)
        }
        
        self.deployment_stats['alert_count'] += 1
        self.alert_callback(alert_data)
    
    def _default_alert_handler(self, alert_data: Dict) -> None:
        """
        Default alert handler (logs to console)
        """
        severity = alert_data['severity'].upper()
        logger.warning(f"🚨 MODEL ALERT [{severity}] - Health Score: {alert_data['health_score']:.3f}")
        for issue in alert_data['issues']:
            logger.warning(f"   - {issue}")
    
    def log_prediction(self, prediction: str, confidence: float, 
                      features: Dict[str, Any], response_time_ms: float = 0.0,
                      actual_result: str = None, user_feedback: float = None) -> None:
        """
        Log prediction and update deployment stats
        """
        self.performance_monitor.log_prediction(
            prediction, confidence, features, response_time_ms, 
            actual_result, user_feedback
        )
        self.deployment_stats['total_predictions'] += 1
    
    def get_deployment_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive deployment dashboard data
        """
        health_metrics = self.performance_monitor.calculate_model_health()
        performance_trends = self.performance_monitor.get_performance_trends()
        
        dashboard = {
            'deployment_info': {
                'deployment_time': self.deployment_stats['deployment_time'].isoformat(),
                'uptime_hours': self.deployment_stats['uptime_seconds'] / 3600,
                'total_predictions': self.deployment_stats['total_predictions'],
                'error_count': self.deployment_stats['error_count'],
                'alert_count': self.deployment_stats['alert_count']
            },
            'current_health': asdict(health_metrics),
            'performance_trends': performance_trends,
            'system_status': self._get_system_status(),
            'recommendations': self._get_recommendations(health_metrics)
        }
        
        return dashboard
    
    def _get_system_status(self) -> Dict[str, str]:
        """
        Get overall system status
        """
        health_metrics = self.performance_monitor.calculate_model_health()
        
        return {
            'overall_status': health_metrics.status,
            'model_performance': 'good' if health_metrics.prediction_accuracy > 0.8 else 'needs_attention',
            'response_time': 'acceptable' if health_metrics.response_time_p95 < 2000 else 'slow',
            'confidence_levels': 'stable' if health_metrics.average_confidence > 0.7 else 'declining',
            'data_quality': 'good' if not health_metrics.feature_drift_detected else 'drift_detected'
        }
    
    def _get_recommendations(self, health_metrics: ModelHealthMetrics) -> List[str]:
        """
        Generate actionable recommendations
        """
        recommendations = []
        
        if health_metrics.prediction_accuracy < 0.8:
            recommendations.append("Consider model retraining - accuracy below acceptable threshold")
        
        if health_metrics.average_confidence < 0.7:
            recommendations.append("Investigate low confidence predictions - may indicate data drift")
        
        if health_metrics.response_time_p95 > 2000:
            recommendations.append("Optimize prediction pipeline - response times too high")
        
        if health_metrics.feature_drift_detected:
            recommendations.append("Data drift detected - schedule model update or feature engineering review")
        
        if health_metrics.error_rate > 0.05:
            recommendations.append("High error rate detected - review input validation and preprocessing")
        
        if not recommendations:
            recommendations.append("System performing well - consider scaling for increased load")
        
        return recommendations

class ABTestingFramework:
    """
    A/B Testing framework for model comparison
    """
    
    def __init__(self):
        self.experiments = {}
        self.results = {}
    
    def create_experiment(self, experiment_id: str, model_a_name: str, 
                         model_b_name: str, traffic_split: float = 0.5) -> None:
        """
        Create new A/B test experiment
        """
        self.experiments[experiment_id] = {
            'model_a': model_a_name,
            'model_b': model_b_name,
            'traffic_split': traffic_split,
            'start_time': datetime.now(),
            'predictions_a': [],
            'predictions_b': [],
            'status': 'active'
        }
        
        logger.info(f"A/B test '{experiment_id}' created: {model_a_name} vs {model_b_name}")
    
    def log_ab_prediction(self, experiment_id: str, model_used: str, 
                         prediction: str, confidence: float, 
                         actual_result: str = None) -> None:
        """
        Log prediction for A/B test
        """
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        
        prediction_record = {
            'prediction': prediction,
            'confidence': confidence,
            'actual_result': actual_result,
            'timestamp': datetime.now()
        }
        
        if model_used == experiment['model_a']:
            experiment['predictions_a'].append(prediction_record)
        elif model_used == experiment['model_b']:
            experiment['predictions_b'].append(prediction_record)
    
    def analyze_ab_test(self, experiment_id: str) -> Dict[str, Any]:
        """
        Analyze A/B test results
        """
        if experiment_id not in self.experiments:
            return {'error': 'Experiment not found'}
        
        experiment = self.experiments[experiment_id]
        
        # Get predictions with actual results
        predictions_a = [p for p in experiment['predictions_a'] if p['actual_result']]
        predictions_b = [p for p in experiment['predictions_b'] if p['actual_result']]
        
        if len(predictions_a) < 30 or len(predictions_b) < 30:
            return {'error': 'Insufficient data for analysis (need 30+ predictions each)'}
        
        # Calculate metrics
        accuracy_a = np.mean([p['prediction'] == p['actual_result'] for p in predictions_a])
        accuracy_b = np.mean([p['prediction'] == p['actual_result'] for p in predictions_b])
        
        confidence_a = np.mean([p['confidence'] for p in predictions_a])
        confidence_b = np.mean([p['confidence'] for p in predictions_b])
        
        # Statistical significance test
        correct_a = sum(1 for p in predictions_a if p['prediction'] == p['actual_result'])
        correct_b = sum(1 for p in predictions_b if p['prediction'] == p['actual_result'])
        
        # Proportions z-test
        p1 = correct_a / len(predictions_a)
        p2 = correct_b / len(predictions_b)
        n1, n2 = len(predictions_a), len(predictions_b)
        
        pooled_p = (correct_a + correct_b) / (n1 + n2)
        se = np.sqrt(pooled_p * (1 - pooled_p) * (1/n1 + 1/n2))
        
        z_score = (p1 - p2) / se if se > 0 else 0
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return {
            'experiment_id': experiment_id,
            'model_a': experiment['model_a'],
            'model_b': experiment['model_b'],
            'sample_sizes': {'a': len(predictions_a), 'b': len(predictions_b)},
            'accuracy': {'a': accuracy_a, 'b': accuracy_b, 'difference': accuracy_a - accuracy_b},
            'confidence': {'a': confidence_a, 'b': confidence_b, 'difference': confidence_a - confidence_b},
            'statistical_test': {
                'z_score': z_score,
                'p_value': p_value,
                'significant': p_value < 0.05,
                'winner': 'A' if accuracy_a > accuracy_b else 'B' if accuracy_b > accuracy_a else 'tie'
            },
            'recommendation': self._get_ab_recommendation(accuracy_a, accuracy_b, p_value)
        }
    
    def _get_ab_recommendation(self, accuracy_a: float, accuracy_b: float, p_value: float) -> str:
        """
        Generate recommendation based on A/B test results
        """
        if p_value >= 0.05:
            return "No statistically significant difference - continue testing or use business metrics to decide"
        
        diff = abs(accuracy_a - accuracy_b)
        if diff < 0.02:
            return "Statistically significant but practically insignificant difference - consider other factors"
        
        winner = "Model A" if accuracy_a > accuracy_b else "Model B"
        return f"{winner} shows significantly better performance - recommend deployment"

def main():
    """
    Demonstration of model monitoring framework
    """
    # Initialize monitoring system
    monitor = ModelDeploymentMonitor()
    
    # Set up baseline statistics (in production, this would be from training data)
    baseline_features = pd.DataFrame({
        'material_encoded': np.random.randint(0, 5, 1000),
        'weight_log': np.random.normal(0.5, 0.3, 1000),
        'transport_encoded': np.random.randint(0, 3, 1000)
    })
    
    monitor.performance_monitor.set_baseline_statistics(baseline_features)
    
    # Start monitoring
    monitor.start_monitoring(check_interval_seconds=60)
    
    # Simulate some predictions
    logger.info("Simulating model predictions...")
    
    for i in range(100):
        # Simulate prediction
        prediction = np.random.choice(['A+', 'A', 'B', 'C', 'D', 'E', 'F'])
        confidence = np.random.uniform(0.6, 0.95)
        features = {
            'material_encoded': np.random.randint(0, 5),
            'weight_log': np.random.normal(0.5, 0.3),
            'transport_encoded': np.random.randint(0, 3)
        }
        response_time_ms = np.random.uniform(100, 500)
        
        # Log prediction
        monitor.log_prediction(prediction, confidence, features, response_time_ms)
        
        time.sleep(0.1)  # Small delay
    
    # Get dashboard
    dashboard = monitor.get_deployment_dashboard()
    
    # Save monitoring results
    results_dir = "/mnt/c/DigSysProj/DSP/backend/ml/monitoring/results"
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dashboard_file = os.path.join(results_dir, f"monitoring_dashboard_{timestamp}.json")
    
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard, f, indent=2, default=str)
    
    logger.info(f"Monitoring dashboard saved to: {dashboard_file}")
    
    # Stop monitoring
    monitor.stop_monitoring_service()
    
    return dashboard

if __name__ == "__main__":
    results = main()