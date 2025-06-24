#!/usr/bin/env python3
"""
🔬 Concept Drift Detection & Adaptive Learning System
===================================================

Theoretical Foundation:
- Statistical Process Control: Control charts for monitoring data quality
- Kolmogorov-Smirnov Test: Non-parametric distribution comparison
- ADWIN Algorithm: Adaptive Windowing for concept drift detection
- Page-Hinkley Test: Sequential change point detection
- Incremental Learning: Online model adaptation

Architecture:
- Multi-method drift detection ensemble
- Adaptive learning with model retraining triggers
- Performance degradation monitoring
- Automated model versioning and rollback
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ks_2samp, mannwhitneyu, entropy
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from collections import deque
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import time
import json
import pickle
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import warnings
from abc import ABC, abstractmethod
import joblib
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DriftDetectionResult:
    """Result of drift detection analysis"""
    drift_detected: bool
    drift_score: float
    drift_type: str  # 'feature', 'label', 'performance'
    affected_features: List[str]
    detection_method: str
    timestamp: str
    confidence: float
    recommended_action: str

@dataclass
class ModelPerformanceMetrics:
    """Model performance tracking"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    timestamp: str
    sample_count: int
    drift_score: float

class DriftDetector(ABC):
    """Abstract base class for drift detection methods"""
    
    @abstractmethod
    def update(self, new_data: np.ndarray) -> bool:
        """Update detector with new data and return drift status"""
        pass
    
    @abstractmethod
    def get_drift_score(self) -> float:
        """Get current drift score (0-1, higher = more drift)"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset detector state"""
        pass

class KolmogorovSmirnovDetector(DriftDetector):
    """
    Kolmogorov-Smirnov test for distribution drift detection
    
    Theory: Two-sample KS test compares empirical distribution functions
    H0: Both samples from same distribution
    H1: Samples from different distributions
    """
    
    def __init__(self, reference_window_size: int = 1000, 
                 detection_window_size: int = 100,
                 significance_level: float = 0.05):
        self.reference_window_size = reference_window_size
        self.detection_window_size = detection_window_size
        self.significance_level = significance_level
        
        self.reference_window = deque(maxlen=reference_window_size)
        self.detection_window = deque(maxlen=detection_window_size)
        self.last_ks_statistic = 0.0
        self.last_p_value = 1.0
    
    def update(self, new_data: np.ndarray) -> bool:
        """Update with new data and check for drift"""
        # Add to detection window
        for sample in new_data:
            self.detection_window.append(sample)
        
        # If reference window not full, add to it as well
        if len(self.reference_window) < self.reference_window_size:
            for sample in new_data:
                self.reference_window.append(sample)
            return False
        
        # Perform KS test when detection window is full
        if len(self.detection_window) >= self.detection_window_size:
            self.last_ks_statistic, self.last_p_value = ks_2samp(
                list(self.reference_window),
                list(self.detection_window)
            )
            
            drift_detected = self.last_p_value < self.significance_level
            
            if drift_detected:
                # Update reference window with recent data
                self.reference_window.clear()
                self.reference_window.extend(list(self.detection_window))
                self.detection_window.clear()
            
            return drift_detected
        
        return False
    
    def get_drift_score(self) -> float:
        """Return drift score based on KS statistic"""
        return self.last_ks_statistic
    
    def reset(self) -> None:
        """Reset detector state"""
        self.reference_window.clear()
        self.detection_window.clear()
        self.last_ks_statistic = 0.0
        self.last_p_value = 1.0

class ADWINDetector(DriftDetector):
    """
    ADWIN (Adaptive Windowing) drift detector
    
    Theory: Maintains variable-length window and detects change when
    difference between sub-windows becomes statistically significant
    """
    
    def __init__(self, delta: float = 0.002):
        self.delta = delta  # Confidence parameter
        self.window = deque()
        self.total = 0.0
        self.variance = 0.0
        self.width = 0
        self.drift_detected = False
    
    def update(self, new_data: np.ndarray) -> bool:
        """Update ADWIN with new data"""
        for value in new_data:
            self._add_element(value)
        
        return self._detect_change()
    
    def _add_element(self, value: float) -> None:
        """Add new element to ADWIN window"""
        self.window.append(value)
        self.width += 1
        
        # Update statistics
        if self.width == 1:
            self.total = value
            self.variance = 0.0
        else:
            old_mean = self.total / (self.width - 1)
            self.total += value
            new_mean = self.total / self.width
            
            # Update variance using Welford's online algorithm
            self.variance = ((self.width - 2) * self.variance + 
                           (value - old_mean) * (value - new_mean)) / (self.width - 1)
    
    def _detect_change(self) -> bool:
        """Detect concept drift using ADWIN algorithm"""
        if self.width < 2:
            return False
        
        # Check all possible cuts in the window
        for i in range(1, self.width):
            left_window = list(self.window)[:i]
            right_window = list(self.window)[i:]
            
            mean_left = np.mean(left_window)
            mean_right = np.mean(right_window)
            
            # Calculate cut threshold
            n0, n1 = len(left_window), len(right_window)
            harmonic_mean = 1.0 / (1.0/n0 + 1.0/n1)
            
            delta_prime = np.sqrt((1.0 / (2.0 * harmonic_mean)) * 
                                np.log(4.0 / self.delta))
            
            # Check if difference is significant
            if abs(mean_left - mean_right) > delta_prime:
                # Drift detected - remove old data
                for _ in range(i):
                    self.window.popleft()
                
                self.width = len(self.window)
                self._recalculate_statistics()
                return True
        
        return False
    
    def _recalculate_statistics(self) -> None:
        """Recalculate statistics after window update"""
        if self.width == 0:
            self.total = 0.0
            self.variance = 0.0
        else:
            window_list = list(self.window)
            self.total = sum(window_list)
            
            if self.width > 1:
                mean = self.total / self.width
                self.variance = np.var(window_list, ddof=1)
            else:
                self.variance = 0.0
    
    def get_drift_score(self) -> float:
        """Return drift score based on window statistics"""
        if self.width < 2:
            return 0.0
        
        # Use normalized variance as drift score
        if self.variance > 0:
            return min(1.0, self.variance / (self.total / self.width + 1e-8))
        return 0.0
    
    def reset(self) -> None:
        """Reset ADWIN detector"""
        self.window.clear()
        self.total = 0.0
        self.variance = 0.0
        self.width = 0

class PageHinkleyDetector(DriftDetector):
    """
    Page-Hinkley test for sequential change point detection
    
    Theory: CUSUM-based method for detecting changes in mean
    """
    
    def __init__(self, min_instances: int = 30, 
                 delta: float = 0.005, threshold: float = 50.0):
        self.min_instances = min_instances
        self.delta = delta
        self.threshold = threshold
        
        self.sum = 0.0
        self.x_mean = 0.0
        self.sample_count = 0
        self.ph_sum = 0.0
        self.ph_min = float('inf')
    
    def update(self, new_data: np.ndarray) -> bool:
        """Update Page-Hinkley test with new data"""
        drift_detected = False
        
        for value in new_data:
            self.sample_count += 1
            self.sum += value
            
            if self.sample_count >= self.min_instances:
                # Update mean
                self.x_mean = self.sum / self.sample_count
                
                # Update Page-Hinkley statistics
                self.ph_sum += (value - self.x_mean - self.delta)
                
                if self.ph_sum < self.ph_min:
                    self.ph_min = self.ph_sum
                
                # Check for drift
                if (self.ph_sum - self.ph_min) > self.threshold:
                    drift_detected = True
                    self.reset()
                    break
        
        return drift_detected
    
    def get_drift_score(self) -> float:
        """Return drift score based on PH statistics"""
        if self.sample_count < self.min_instances:
            return 0.0
        
        return min(1.0, (self.ph_sum - self.ph_min) / self.threshold)
    
    def reset(self) -> None:
        """Reset Page-Hinkley detector"""
        self.sum = 0.0
        self.x_mean = 0.0
        self.sample_count = 0
        self.ph_sum = 0.0
        self.ph_min = float('inf')

class ConceptDriftMonitor:
    """
    Comprehensive concept drift monitoring system
    
    Features:
    1. Multi-method drift detection ensemble
    2. Feature-wise and label drift detection
    3. Performance degradation monitoring
    4. Automated model adaptation triggers
    """
    
    def __init__(self, 
                 feature_names: List[str],
                 class_names: List[str],
                 detection_methods: Optional[List[str]] = None):
        """
        Initialize concept drift monitor
        
        Args:
            feature_names: Names of input features
            class_names: Names of target classes
            detection_methods: List of detection methods to use
        """
        self.feature_names = feature_names
        self.class_names = class_names
        self.num_features = len(feature_names)
        
        # Initialize detection methods
        detection_methods = detection_methods or ['ks', 'adwin', 'page_hinkley']
        self.detectors = self._initialize_detectors(detection_methods)
        
        # Performance monitoring
        self.performance_history = deque(maxlen=1000)
        self.performance_baseline = None
        self.performance_threshold = 0.05  # 5% degradation threshold
        
        # Drift detection results
        self.drift_history = []
        self.last_drift_detection = None
        
        # Threading for concurrent detection
        self.detection_lock = threading.Lock()
        
        logger.info(f"Concept drift monitor initialized with {len(self.detectors)} detection methods")
    
    def _initialize_detectors(self, methods: List[str]) -> Dict[str, Dict[str, DriftDetector]]:
        """Initialize drift detectors for each feature"""
        detectors = {method: {} for method in methods}
        
        for method in methods:
            # Create detector for each feature
            for feature_name in self.feature_names:
                if method == 'ks':
                    detectors[method][feature_name] = KolmogorovSmirnovDetector()
                elif method == 'adwin':
                    detectors[method][feature_name] = ADWINDetector()
                elif method == 'page_hinkley':
                    detectors[method][feature_name] = PageHinkleyDetector()
        
        return detectors
    
    def update(self, X: np.ndarray, y: Optional[np.ndarray] = None,
               y_pred: Optional[np.ndarray] = None,
               model_confidence: Optional[np.ndarray] = None) -> DriftDetectionResult:
        """
        Update drift monitor with new data
        
        Args:
            X: Feature matrix
            y: True labels (optional)
            y_pred: Predicted labels (optional)
            model_confidence: Prediction confidence scores (optional)
            
        Returns:
            DriftDetectionResult with detection summary
        """
        with self.detection_lock:
            drift_results = []
            
            # 1. Feature drift detection
            feature_drift = self._detect_feature_drift(X)
            if feature_drift:
                drift_results.append(feature_drift)
            
            # 2. Label drift detection (if true labels available)
            if y is not None:
                label_drift = self._detect_label_drift(y)
                if label_drift:
                    drift_results.append(label_drift)
            
            # 3. Performance drift detection (if predictions available)
            if y is not None and y_pred is not None:
                performance_drift = self._detect_performance_drift(y, y_pred, model_confidence)
                if performance_drift:
                    drift_results.append(performance_drift)
            
            # Aggregate results
            if drift_results:
                # Return most severe drift
                most_severe_drift = max(drift_results, key=lambda x: x.drift_score)
                self.drift_history.append(most_severe_drift)
                self.last_drift_detection = most_severe_drift
                return most_severe_drift
            else:
                # No drift detected
                no_drift = DriftDetectionResult(
                    drift_detected=False,
                    drift_score=0.0,
                    drift_type='none',
                    affected_features=[],
                    detection_method='ensemble',
                    timestamp=datetime.now().isoformat(),
                    confidence=0.0,
                    recommended_action='continue_monitoring'
                )
                return no_drift
    
    def _detect_feature_drift(self, X: np.ndarray) -> Optional[DriftDetectionResult]:
        """Detect drift in input features"""
        affected_features = []
        drift_scores = []
        
        # Check each feature with each detection method
        for method_name, method_detectors in self.detectors.items():
            for i, feature_name in enumerate(self.feature_names):
                detector = method_detectors[feature_name]
                
                # Extract feature values
                feature_values = X[:, i]
                
                # Update detector
                drift_detected = detector.update(feature_values)
                
                if drift_detected:
                    drift_score = detector.get_drift_score()
                    affected_features.append(feature_name)
                    drift_scores.append(drift_score)
                    
                    logger.warning(f"Feature drift detected in '{feature_name}' using {method_name} "
                                 f"(score: {drift_score:.4f})")
        
        if affected_features:
            # Remove duplicates and calculate aggregate score
            affected_features = list(set(affected_features))
            avg_drift_score = np.mean(drift_scores)
            
            return DriftDetectionResult(
                drift_detected=True,
                drift_score=avg_drift_score,
                drift_type='feature',
                affected_features=affected_features,
                detection_method='ensemble',
                timestamp=datetime.now().isoformat(),
                confidence=min(1.0, avg_drift_score * 2),  # Scale confidence
                recommended_action='retrain_model' if avg_drift_score > 0.5 else 'monitor_closely'
            )
        
        return None
    
    def _detect_label_drift(self, y: np.ndarray) -> Optional[DriftDetectionResult]:
        """Detect drift in label distribution"""
        # Simple approach: check if label distribution has changed significantly
        current_distribution = np.bincount(y, minlength=len(self.class_names))
        current_distribution = current_distribution / current_distribution.sum()
        
        if hasattr(self, 'reference_label_distribution'):
            # Use Jensen-Shannon divergence to measure distribution difference
            js_divergence = self._jensen_shannon_divergence(
                self.reference_label_distribution,
                current_distribution
            )
            
            # Threshold for significant label drift
            if js_divergence > 0.1:  # Configurable threshold
                return DriftDetectionResult(
                    drift_detected=True,
                    drift_score=js_divergence,
                    drift_type='label',
                    affected_features=[],
                    detection_method='jensen_shannon',
                    timestamp=datetime.now().isoformat(),
                    confidence=min(1.0, js_divergence * 5),
                    recommended_action='retrain_model'
                )
        else:
            # Store as reference distribution
            self.reference_label_distribution = current_distribution
        
        return None
    
    def _detect_performance_drift(self, y_true: np.ndarray, y_pred: np.ndarray,
                                confidence: Optional[np.ndarray] = None) -> Optional[DriftDetectionResult]:
        """Detect performance degradation"""
        # Calculate current performance
        current_accuracy = accuracy_score(y_true, y_pred)
        
        # Store performance metrics
        performance_metrics = ModelPerformanceMetrics(
            accuracy=current_accuracy,
            precision=0.0,  # Would calculate from classification_report
            recall=0.0,
            f1_score=0.0,
            timestamp=datetime.now().isoformat(),
            sample_count=len(y_true),
            drift_score=0.0
        )
        self.performance_history.append(performance_metrics)
        
        # Check for performance drift
        if self.performance_baseline is None:
            self.performance_baseline = current_accuracy
            return None
        
        performance_drop = self.performance_baseline - current_accuracy
        
        if performance_drop > self.performance_threshold:
            # Significant performance degradation detected
            drift_score = performance_drop / self.performance_baseline
            
            return DriftDetectionResult(
                drift_detected=True,
                drift_score=drift_score,
                drift_type='performance',
                affected_features=[],
                detection_method='performance_monitoring',
                timestamp=datetime.now().isoformat(),
                confidence=min(1.0, drift_score * 3),
                recommended_action='retrain_model'
            )
        
        return None
    
    def _jensen_shannon_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Jensen-Shannon divergence between two distributions"""
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        p = p + epsilon
        q = q + epsilon
        
        # Normalize to ensure they sum to 1
        p = p / p.sum()
        q = q / q.sum()
        
        # Calculate JS divergence
        m = 0.5 * (p + q)
        js_div = 0.5 * entropy(p, m) + 0.5 * entropy(q, m)
        
        return js_div
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get comprehensive drift detection summary"""
        recent_drifts = [d for d in self.drift_history 
                        if datetime.fromisoformat(d.timestamp) > 
                           datetime.now() - timedelta(days=7)]
        
        drift_by_type = {}
        for drift in recent_drifts:
            drift_type = drift.drift_type
            if drift_type not in drift_by_type:
                drift_by_type[drift_type] = []
            drift_by_type[drift_type].append(drift)
        
        # Performance statistics
        recent_performance = list(self.performance_history)[-100:]  # Last 100 samples
        avg_recent_accuracy = np.mean([p.accuracy for p in recent_performance]) if recent_performance else 0.0
        
        return {
            'total_drifts_detected': len(self.drift_history),
            'recent_drifts_7days': len(recent_drifts),
            'drift_by_type': {
                drift_type: len(drifts) for drift_type, drifts in drift_by_type.items()
            },
            'last_drift_detection': asdict(self.last_drift_detection) if self.last_drift_detection else None,
            'performance_baseline': self.performance_baseline,
            'recent_avg_accuracy': avg_recent_accuracy,
            'performance_history_size': len(self.performance_history),
            'active_detectors': list(self.detectors.keys())
        }
    
    def reset_detectors(self) -> None:
        """Reset all drift detectors"""
        logger.info("Resetting all drift detectors...")
        
        for method_detectors in self.detectors.values():
            for detector in method_detectors.values():
                detector.reset()
        
        # Reset performance baseline
        self.performance_baseline = None
        
        logger.info("All drift detectors reset")

class AdaptiveLearningSystem:
    """
    Adaptive learning system with automatic model retraining
    
    Features:
    1. Concept drift detection integration
    2. Incremental learning capabilities
    3. Model versioning and rollback
    4. Performance monitoring and triggers
    """
    
    def __init__(self, 
                 base_model: BaseEstimator,
                 feature_names: List[str],
                 class_names: List[str],
                 retrain_threshold: float = 0.3):
        """
        Initialize adaptive learning system
        
        Args:
            base_model: Base ML model to adapt
            feature_names: Names of input features
            class_names: Names of target classes
            retrain_threshold: Drift score threshold for retraining
        """
        self.base_model = base_model
        self.feature_names = feature_names
        self.class_names = class_names
        self.retrain_threshold = retrain_threshold
        
        # Initialize drift monitor
        self.drift_monitor = ConceptDriftMonitor(feature_names, class_names)
        
        # Model versioning
        self.model_versions = []
        self.current_model_version = 0
        
        # Training data buffer for retraining
        self.training_buffer = deque(maxlen=10000)  # Keep last 10k samples
        
        # Adaptation statistics
        self.adaptation_history = []
        
        logger.info("Adaptive learning system initialized")
    
    def update(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Update system with new data and adapt if necessary
        
        Args:
            X: Feature matrix
            y: True labels
            
        Returns:
            Update summary with adaptation decisions
        """
        # Store data in training buffer
        for i in range(len(X)):
            self.training_buffer.append((X[i], y[i]))
        
        # Get predictions for drift detection
        y_pred = self.base_model.predict(X)
        y_pred_proba = None
        if hasattr(self.base_model, 'predict_proba'):
            y_pred_proba = self.base_model.predict_proba(X)
        
        # Update drift monitor
        drift_result = self.drift_monitor.update(
            X, y, y_pred, 
            y_pred_proba.max(axis=1) if y_pred_proba is not None else None
        )
        
        # Check if adaptation is needed
        adaptation_needed = (
            drift_result.drift_detected and 
            drift_result.drift_score > self.retrain_threshold
        )
        
        update_summary = {
            'samples_processed': len(X),
            'drift_detected': drift_result.drift_detected,
            'drift_score': drift_result.drift_score,
            'drift_type': drift_result.drift_type,
            'adaptation_triggered': adaptation_needed,
            'model_version': self.current_model_version
        }
        
        if adaptation_needed:
            logger.info(f"Adaptation triggered: {drift_result.drift_type} drift "
                       f"(score: {drift_result.drift_score:.4f})")
            
            adaptation_result = self._adapt_model()
            update_summary.update(adaptation_result)
        
        return update_summary
    
    def _adapt_model(self) -> Dict[str, Any]:
        """Adapt model to concept drift"""
        adaptation_start = time.time()
        
        # Prepare training data from buffer
        if len(self.training_buffer) < 100:  # Minimum samples for retraining
            logger.warning("Insufficient data for model adaptation")
            return {'adaptation_success': False, 'reason': 'insufficient_data'}
        
        # Extract features and labels from buffer
        X_buffer = np.array([sample[0] for sample in self.training_buffer])
        y_buffer = np.array([sample[1] for sample in self.training_buffer])
        
        # Split into train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_buffer, y_buffer, test_size=0.2, random_state=42, stratify=y_buffer
        )
        
        try:
            # Save current model version
            self._save_model_version()
            
            # Retrain model
            logger.info(f"Retraining model with {len(X_train)} samples...")
            
            # Clone and retrain model
            new_model = type(self.base_model)(**self.base_model.get_params())
            new_model.fit(X_train, y_train)
            
            # Validate new model
            val_accuracy = accuracy_score(y_val, new_model.predict(X_val))
            
            # Compare with previous model performance
            prev_accuracy = accuracy_score(y_val, self.base_model.predict(X_val))
            
            if val_accuracy >= prev_accuracy * 0.95:  # Allow 5% degradation
                # Accept new model
                self.base_model = new_model
                self.current_model_version += 1
                
                # Reset drift detectors
                self.drift_monitor.reset_detectors()
                
                adaptation_time = time.time() - adaptation_start
                
                adaptation_record = {
                    'timestamp': datetime.now().isoformat(),
                    'trigger_reason': 'concept_drift',
                    'training_samples': len(X_train),
                    'validation_accuracy': val_accuracy,
                    'previous_accuracy': prev_accuracy,
                    'improvement': val_accuracy - prev_accuracy,
                    'adaptation_time': adaptation_time,
                    'model_version': self.current_model_version
                }
                self.adaptation_history.append(adaptation_record)
                
                logger.info(f"Model adaptation successful: "
                          f"accuracy {prev_accuracy:.4f} → {val_accuracy:.4f} "
                          f"(version {self.current_model_version})")
                
                return {
                    'adaptation_success': True,
                    'new_accuracy': val_accuracy,
                    'accuracy_improvement': val_accuracy - prev_accuracy,
                    'adaptation_time': adaptation_time,
                    'new_model_version': self.current_model_version
                }
            else:
                # Reject new model and potentially rollback
                logger.warning(f"New model performance degraded: "
                             f"{val_accuracy:.4f} vs {prev_accuracy:.4f}. "
                             f"Keeping current model.")
                
                return {
                    'adaptation_success': False,
                    'reason': 'performance_degradation',
                    'new_accuracy': val_accuracy,
                    'current_accuracy': prev_accuracy
                }
                
        except Exception as e:
            logger.error(f"Model adaptation failed: {e}")
            return {
                'adaptation_success': False,
                'reason': 'training_error',
                'error': str(e)
            }
    
    def _save_model_version(self) -> None:
        """Save current model version for potential rollback"""
        model_copy = pickle.loads(pickle.dumps(self.base_model))  # Deep copy
        
        version_info = {
            'model': model_copy,
            'version': self.current_model_version,
            'timestamp': datetime.now().isoformat(),
            'performance_baseline': self.drift_monitor.performance_baseline
        }
        
        self.model_versions.append(version_info)
        
        # Keep only last 5 versions
        if len(self.model_versions) > 5:
            self.model_versions.pop(0)
    
    def rollback_model(self, version: Optional[int] = None) -> bool:
        """
        Rollback to previous model version
        
        Args:
            version: Specific version to rollback to (None for previous)
            
        Returns:
            Success status
        """
        if not self.model_versions:
            logger.warning("No model versions available for rollback")
            return False
        
        if version is None:
            # Rollback to most recent version
            target_version_info = self.model_versions[-1]
        else:
            # Find specific version
            target_version_info = None
            for version_info in self.model_versions:
                if version_info['version'] == version:
                    target_version_info = version_info
                    break
            
            if target_version_info is None:
                logger.warning(f"Model version {version} not found")
                return False
        
        # Restore model
        self.base_model = target_version_info['model']
        self.current_model_version = target_version_info['version']
        
        # Restore performance baseline
        if 'performance_baseline' in target_version_info:
            self.drift_monitor.performance_baseline = target_version_info['performance_baseline']
        
        logger.info(f"Model rolled back to version {self.current_model_version}")
        return True
    
    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get comprehensive adaptation summary"""
        drift_summary = self.drift_monitor.get_drift_summary()
        
        return {
            'current_model_version': self.current_model_version,
            'total_adaptations': len(self.adaptation_history),
            'available_rollback_versions': len(self.model_versions),
            'training_buffer_size': len(self.training_buffer),
            'drift_summary': drift_summary,
            'recent_adaptations': self.adaptation_history[-5:],  # Last 5 adaptations
            'retrain_threshold': self.retrain_threshold
        }

def main():
    """Example usage and testing"""
    print("Concept Drift Detection & Adaptive Learning System implementation complete!")
    
    # Example usage:
    # feature_names = ['material', 'weight', 'transport', 'origin', ...]
    # class_names = ['A+', 'A', 'B', 'C', 'D', 'E', 'F']
    # 
    # # Initialize base model
    # base_model = xgb.XGBClassifier(random_state=42)
    # 
    # # Initialize adaptive system
    # adaptive_system = AdaptiveLearningSystem(
    #     base_model=base_model,
    #     feature_names=feature_names,
    #     class_names=class_names,
    #     retrain_threshold=0.3
    # )
    # 
    # # Simulate data stream with concept drift
    # for batch_X, batch_y in data_stream:
    #     update_summary = adaptive_system.update(batch_X, batch_y)
    #     
    #     if update_summary['adaptation_triggered']:
    #         print(f"Model adapted: version {update_summary['new_model_version']}")

if __name__ == "__main__":
    main()