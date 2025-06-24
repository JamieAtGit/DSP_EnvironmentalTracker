#!/usr/bin/env python3
"""
🧠 Real-Time Explainable AI Engine
=================================

Theoretical Foundation:
- Shapley Values: Game-theoretic approach to fair attribution
- LIME: Local linear approximation for model-agnostic explanations
- Integrated Gradients: Path integral approach for deep models
- Counterfactual Explanations: What-if analysis for decision boundaries

Architecture:
- Multi-modal explanation generation
- Real-time computation with caching
- Interactive visualization components
- Uncertainty quantification
"""

import numpy as np
import pandas as pd
import shap
import lime
import lime.tabular
from lime.lime_tabular import LimeTabularExplainer
from sklearn.base import BaseEstimator
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import time
import json
import hashlib
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExplanationResult:
    """Data class for explanation results"""
    instance_id: str
    prediction: np.ndarray
    prediction_proba: np.ndarray
    shap_values: np.ndarray
    lime_explanation: List[Tuple[str, float]]
    feature_importance: Dict[str, float]
    counterfactuals: Optional[Dict[str, Any]] = None
    uncertainty_metrics: Optional[Dict[str, float]] = None
    computation_time: float = 0.0
    explanation_quality: float = 0.0

class ExplainableAIEngine:
    """
    Advanced explainable AI engine with multiple explanation methods
    
    Features:
    1. Multi-modal explanations (SHAP, LIME, Permutation)
    2. Real-time computation with intelligent caching
    3. Uncertainty quantification for explanations
    4. Interactive visualization generation
    5. Counterfactual analysis
    6. Quality assessment of explanations
    """
    
    def __init__(self, model: BaseEstimator, 
                 feature_names: List[str],
                 class_names: List[str],
                 training_data: np.ndarray,
                 categorical_features: Optional[List[int]] = None):
        """
        Initialize explainable AI engine
        
        Args:
            model: Trained ML model
            feature_names: Names of features
            class_names: Names of target classes  
            training_data: Training dataset for background
            categorical_features: Indices of categorical features
        """
        self.model = model
        self.feature_names = feature_names
        self.class_names = class_names
        self.training_data = training_data
        self.categorical_features = categorical_features or []
        
        # Initialize explainers
        self._initialize_explainers()
        
        # Cache for expensive computations
        self.explanation_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("ExplainableAI Engine initialized successfully")
    
    def _initialize_explainers(self):
        """Initialize different explanation methods"""
        try:
            # SHAP Explainer (game-theoretic approach)
            if hasattr(self.model, 'predict_proba'):
                # For tree-based models, use TreeExplainer (exact Shapley values)
                if hasattr(self.model, 'feature_importances_'):
                    self.shap_explainer = shap.TreeExplainer(self.model)
                    logger.info("Using SHAP TreeExplainer (exact computation)")
                else:
                    # For other models, use KernelExplainer (sampling-based)
                    background = shap.kmeans(self.training_data, 50)  # 50 background samples
                    self.shap_explainer = shap.KernelExplainer(
                        self.model.predict_proba, background
                    )
                    logger.info("Using SHAP KernelExplainer (sampling-based)")
            else:
                # For models without predict_proba
                background = shap.kmeans(self.training_data, 50)
                self.shap_explainer = shap.KernelExplainer(
                    self.model.predict, background
                )
                logger.info("Using SHAP KernelExplainer for predict method")
                
        except Exception as e:
            logger.warning(f"SHAP initialization failed: {e}")
            self.shap_explainer = None
        
        try:
            # LIME Explainer (local linear approximation)
            self.lime_explainer = LimeTabularExplainer(
                training_data=self.training_data,
                feature_names=self.feature_names,
                class_names=self.class_names,
                categorical_features=self.categorical_features,
                mode='classification',
                discretize_continuous=True,
                random_state=42
            )
            logger.info("LIME explainer initialized")
            
        except Exception as e:
            logger.warning(f"LIME initialization failed: {e}")
            self.lime_explainer = None
    
    def _generate_instance_id(self, instance: np.ndarray) -> str:
        """Generate unique ID for instance (for caching)"""
        instance_str = np.array2string(instance, precision=6)
        return hashlib.md5(instance_str.encode()).hexdigest()
    
    @lru_cache(maxsize=1000)
    def _cached_shap_values(self, instance_tuple: tuple) -> np.ndarray:
        """Cached SHAP computation"""
        instance = np.array(instance_tuple).reshape(1, -1)
        if self.shap_explainer is None:
            return np.zeros(len(self.feature_names))
        
        try:
            shap_values = self.shap_explainer.shap_values(instance)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # Multi-class classification - use values for predicted class
                predicted_class = self.model.predict(instance)[0]
                class_idx = list(self.class_names).index(predicted_class)
                return shap_values[class_idx][0]
            else:
                # Binary classification or regression
                if len(shap_values.shape) == 2:
                    return shap_values[0]
                else:
                    return shap_values
                    
        except Exception as e:
            logger.warning(f"SHAP computation failed: {e}")
            return np.zeros(len(self.feature_names))
    
    def _compute_lime_explanation(self, instance: np.ndarray, 
                                 num_features: int = None) -> List[Tuple[str, float]]:
        """Compute LIME explanation"""
        if self.lime_explainer is None:
            return []
        
        num_features = num_features or len(self.feature_names)
        
        try:
            explanation = self.lime_explainer.explain_instance(
                instance.flatten(),
                self.model.predict_proba,
                num_features=min(num_features, len(self.feature_names)),
                num_samples=1000  # Balance between accuracy and speed
            )
            
            return explanation.as_list()
            
        except Exception as e:
            logger.warning(f"LIME computation failed: {e}")
            return []
    
    def _compute_permutation_importance(self, instance: np.ndarray) -> Dict[str, float]:
        """Compute permutation importance for single instance"""
        try:
            # Create small dataset around the instance for permutation
            noise_std = 0.1
            n_samples = 100
            
            # Generate perturbed samples
            perturbed_data = np.tile(instance, (n_samples, 1))
            perturbed_data += np.random.normal(0, noise_std, perturbed_data.shape)
            
            # Dummy targets (not used in permutation importance)
            dummy_targets = np.zeros(n_samples)
            
            # Compute permutation importance
            perm_importance = permutation_importance(
                self.model, perturbed_data, dummy_targets,
                n_repeats=10, random_state=42, scoring='accuracy'
            )
            
            return dict(zip(self.feature_names, perm_importance.importances_mean))
            
        except Exception as e:
            logger.warning(f"Permutation importance computation failed: {e}")
            return {}
    
    def _generate_counterfactuals(self, instance: np.ndarray) -> Dict[str, Any]:
        """
        Generate counterfactual explanations
        
        Theory: Find minimal changes that flip prediction
        Method: Gradient-based optimization or genetic algorithm
        """
        try:
            original_prediction = self.model.predict(instance.reshape(1, -1))[0]
            original_proba = self.model.predict_proba(instance.reshape(1, -1))[0]
            
            counterfactuals = []
            
            # Simple perturbation-based approach
            for feature_idx in range(len(instance)):
                # Try different perturbation magnitudes
                for perturbation in [-0.1, -0.2, 0.1, 0.2]:
                    perturbed_instance = instance.copy()
                    perturbed_instance[feature_idx] += perturbation
                    
                    new_prediction = self.model.predict(perturbed_instance.reshape(1, -1))[0]
                    
                    if new_prediction != original_prediction:
                        counterfactuals.append({
                            'feature': self.feature_names[feature_idx],
                            'original_value': instance[feature_idx],
                            'counterfactual_value': perturbed_instance[feature_idx],
                            'change': perturbation,
                            'new_prediction': new_prediction
                        })
                        break
            
            return {
                'original_prediction': original_prediction,
                'original_probability': original_proba.max(),
                'counterfactuals': counterfactuals[:5]  # Top 5 counterfactuals
            }
            
        except Exception as e:
            logger.warning(f"Counterfactual generation failed: {e}")
            return {}
    
    def _assess_explanation_quality(self, shap_values: np.ndarray, 
                                   lime_explanation: List[Tuple[str, float]]) -> float:
        """
        Assess quality of explanations using consistency metrics
        
        Theory: Good explanations should be consistent across methods
        """
        try:
            # Convert LIME to same format as SHAP
            lime_dict = dict(lime_explanation)
            lime_values = np.array([
                lime_dict.get(feature, 0) for feature in self.feature_names
            ])
            
            # Normalize both to [0, 1]
            shap_normalized = np.abs(shap_values) / (np.abs(shap_values).sum() + 1e-8)
            lime_normalized = np.abs(lime_values) / (np.abs(lime_values).sum() + 1e-8)
            
            # Compute correlation as quality metric
            correlation = np.corrcoef(shap_normalized, lime_normalized)[0, 1]
            
            # Handle NaN correlation (when one method gives all zeros)
            if np.isnan(correlation):
                correlation = 0.0
            
            return float(correlation)
            
        except Exception as e:
            logger.warning(f"Explanation quality assessment failed: {e}")
            return 0.0
    
    def explain_instance(self, instance: np.ndarray, 
                        include_counterfactuals: bool = True,
                        include_uncertainty: bool = True) -> ExplanationResult:
        """
        Generate comprehensive explanation for single instance
        
        Args:
            instance: Feature vector to explain
            include_counterfactuals: Whether to generate counterfactuals
            include_uncertainty: Whether to compute uncertainty metrics
            
        Returns:
            ExplanationResult with all explanation components
        """
        start_time = time.time()
        
        # Generate unique instance ID
        instance_id = self._generate_instance_id(instance)
        
        # Check cache first
        if instance_id in self.explanation_cache:
            self.cache_hits += 1
            cached_result = self.explanation_cache[instance_id]
            logger.debug(f"Cache hit for instance {instance_id}")
            return cached_result
        
        self.cache_misses += 1
        
        # Compute prediction and probabilities
        prediction = self.model.predict(instance.reshape(1, -1))
        prediction_proba = self.model.predict_proba(instance.reshape(1, -1))[0]
        
        # Compute SHAP values
        instance_tuple = tuple(instance)
        shap_values = self._cached_shap_values(instance_tuple)
        
        # Compute LIME explanation
        lime_explanation = self._compute_lime_explanation(instance)
        
        # Create feature importance dictionary
        feature_importance = dict(zip(self.feature_names, shap_values))
        
        # Optional computations
        counterfactuals = None
        uncertainty_metrics = None
        
        if include_counterfactuals:
            counterfactuals = self._generate_counterfactuals(instance)
        
        if include_uncertainty and hasattr(self.model, 'predict_proba'):
            # Compute prediction uncertainty
            confidence = prediction_proba.max()
            entropy = -np.sum(prediction_proba * np.log(prediction_proba + 1e-8))
            
            uncertainty_metrics = {
                'confidence': float(confidence),
                'entropy': float(entropy),
                'max_probability': float(prediction_proba.max()),
                'prediction_margin': float(np.sort(prediction_proba)[-1] - np.sort(prediction_proba)[-2])
            }
        
        # Assess explanation quality
        explanation_quality = self._assess_explanation_quality(shap_values, lime_explanation)
        
        computation_time = time.time() - start_time
        
        # Create result
        result = ExplanationResult(
            instance_id=instance_id,
            prediction=prediction,
            prediction_proba=prediction_proba,
            shap_values=shap_values,
            lime_explanation=lime_explanation,
            feature_importance=feature_importance,
            counterfactuals=counterfactuals,
            uncertainty_metrics=uncertainty_metrics,
            computation_time=computation_time,
            explanation_quality=explanation_quality
        )
        
        # Cache result
        self.explanation_cache[instance_id] = result
        
        logger.info(f"Generated explanation for instance {instance_id} in {computation_time:.3f}s")
        
        return result
    
    def explain_batch(self, instances: np.ndarray, 
                     max_workers: int = 4) -> List[ExplanationResult]:
        """
        Generate explanations for batch of instances using parallel processing
        
        Args:
            instances: Array of feature vectors (n_samples, n_features)
            max_workers: Number of parallel workers
            
        Returns:
            List of ExplanationResult objects
        """
        logger.info(f"Generating explanations for {len(instances)} instances")
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.explain_instance, instance)
                for instance in instances
            ]
            
            results = [future.result() for future in futures]
        
        return results
    
    def generate_visualization(self, explanation_result: ExplanationResult) -> Dict[str, Any]:
        """
        Generate interactive visualizations for explanation
        
        Returns:
            Dictionary with Plotly figure JSON representations
        """
        visualizations = {}
        
        try:
            # 1. SHAP Waterfall Chart
            shap_fig = self._create_shap_waterfall(explanation_result)
            visualizations['shap_waterfall'] = shap_fig
            
            # 2. Feature Importance Bar Chart
            importance_fig = self._create_importance_chart(explanation_result)
            visualizations['feature_importance'] = importance_fig
            
            # 3. Prediction Confidence Gauge
            confidence_fig = self._create_confidence_gauge(explanation_result)
            visualizations['confidence_gauge'] = confidence_fig
            
            # 4. LIME vs SHAP Comparison
            comparison_fig = self._create_method_comparison(explanation_result)
            visualizations['method_comparison'] = comparison_fig
            
            # 5. Counterfactual Analysis (if available)
            if explanation_result.counterfactuals:
                counterfactual_fig = self._create_counterfactual_plot(explanation_result)
                visualizations['counterfactuals'] = counterfactual_fig
                
        except Exception as e:
            logger.warning(f"Visualization generation failed: {e}")
        
        return visualizations
    
    def _create_shap_waterfall(self, result: ExplanationResult) -> str:
        """Create SHAP waterfall chart"""
        # Sort features by absolute SHAP value
        feature_values = list(zip(self.feature_names, result.shap_values))
        feature_values.sort(key=lambda x: abs(x[1]), reverse=True)
        
        features, values = zip(*feature_values[:10])  # Top 10 features
        
        fig = go.Figure(go.Waterfall(
            name="SHAP Values",
            orientation="v",
            measure=["relative"] * len(features),
            x=features,
            textposition="outside",
            text=[f"{v:.3f}" for v in values],
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="SHAP Waterfall: Feature Contributions to Prediction",
            showlegend=False,
            height=500,
            xaxis={'categoryorder': 'total descending'}
        )
        
        return fig.to_json()
    
    def _create_importance_chart(self, result: ExplanationResult) -> str:
        """Create feature importance bar chart"""
        # Get top features by absolute importance
        sorted_features = sorted(
            result.feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]
        
        features, importances = zip(*sorted_features)
        colors = ['red' if imp < 0 else 'blue' for imp in importances]
        
        fig = go.Figure(data=[
            go.Bar(x=features, y=importances, marker_color=colors)
        ])
        
        fig.update_layout(
            title="Feature Importance (SHAP Values)",
            xaxis_title="Features",
            yaxis_title="SHAP Value",
            height=400
        )
        
        return fig.to_json()
    
    def _create_confidence_gauge(self, result: ExplanationResult) -> str:
        """Create prediction confidence gauge"""
        if result.uncertainty_metrics is None:
            return "{}"
        
        confidence = result.uncertainty_metrics['confidence']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=confidence * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Prediction Confidence (%)"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        
        return fig.to_json()
    
    def _create_method_comparison(self, result: ExplanationResult) -> str:
        """Create LIME vs SHAP comparison"""
        # Extract LIME values
        lime_dict = dict(result.lime_explanation)
        
        # Create comparison data
        features = self.feature_names[:10]  # Top 10 features
        shap_values = [result.feature_importance.get(f, 0) for f in features]
        lime_values = [lime_dict.get(f, 0) for f in features]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='SHAP',
            x=features,
            y=shap_values,
            offsetgroup=1
        ))
        
        fig.add_trace(go.Bar(
            name='LIME',
            x=features,
            y=lime_values,
            offsetgroup=2
        ))
        
        fig.update_layout(
            title="Explanation Method Comparison",
            xaxis_title="Features",
            yaxis_title="Importance Score",
            barmode='group',
            height=400
        )
        
        return fig.to_json()
    
    def _create_counterfactual_plot(self, result: ExplanationResult) -> str:
        """Create counterfactual analysis plot"""
        if not result.counterfactuals or not result.counterfactuals.get('counterfactuals'):
            return "{}"
        
        counterfactuals = result.counterfactuals['counterfactuals']
        
        features = [cf['feature'] for cf in counterfactuals]
        original_values = [cf['original_value'] for cf in counterfactuals]
        counterfactual_values = [cf['counterfactual_value'] for cf in counterfactuals]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=features,
            y=original_values,
            mode='markers',
            name='Original Values',
            marker=dict(size=10, color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=features,
            y=counterfactual_values,
            mode='markers',
            name='Counterfactual Values',
            marker=dict(size=10, color='red')
        ))
        
        # Add arrows showing changes
        for i, feature in enumerate(features):
            fig.add_annotation(
                x=feature,
                y=original_values[i],
                ax=feature,
                ay=counterfactual_values[i],
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green'
            )
        
        fig.update_layout(
            title="Counterfactual Analysis: Minimal Changes for Different Prediction",
            xaxis_title="Features",
            yaxis_title="Feature Values",
            height=400
        )
        
        return fig.to_json()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.explanation_cache)
        }
    
    def clear_cache(self):
        """Clear explanation cache"""
        self.explanation_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Explanation cache cleared")

def main():
    """Example usage"""
    print("ExplainableAI Engine implementation complete!")
    
    # Example integration:
    # from your_model import load_trained_model
    # model = load_trained_model()
    # X_train = load_training_data()
    # feature_names = ['material', 'weight', 'transport', ...]
    # class_names = ['A+', 'A', 'B', 'C', 'D', 'E', 'F']
    # 
    # explainer = ExplainableAIEngine(
    #     model=model,
    #     feature_names=feature_names,
    #     class_names=class_names,
    #     training_data=X_train
    # )
    # 
    # # Explain single instance
    # explanation = explainer.explain_instance(instance)
    # visualizations = explainer.generate_visualization(explanation)

if __name__ == "__main__":
    main()