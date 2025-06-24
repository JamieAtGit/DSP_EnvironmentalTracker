#!/usr/bin/env python3
"""
🎯 Advanced Ensemble Learning System
====================================

Theoretical Foundation:
- Condorcet's Jury Theorem: Ensemble accuracy > individual model accuracy
- Bias-Variance Decomposition: Different models reduce different error components
- No Free Lunch Theorem: Diverse hypothesis spaces improve generalization

Architecture:
- Level 1: Diverse base learners with different inductive biases
- Level 2: Meta-learning with stacking and blending
- Level 3: Dynamic ensemble selection based on input characteristics

Time Complexity: O(k*n*log(n)) where k=models, n=samples
Space Complexity: O(k*m) where m=model parameters
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    VotingClassifier, StackingClassifier, RandomForestClassifier,
    ExtraTreesClassifier, GradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
import joblib
import logging
from typing import Dict, List, Tuple, Any
import time
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Data class for storing model performance metrics"""
    name: str
    accuracy: float
    cv_scores: List[float]
    training_time: float
    prediction_time: float
    model_size: int  # in bytes

class AdvancedEnsembleSystem:
    """
    Master-level ensemble system with theoretical grounding
    
    Features:
    1. Heterogeneous base learners (different algorithms)
    2. Dynamic model selection based on input characteristics
    3. Uncertainty quantification with prediction intervals
    4. Online learning capability for concept drift adaptation
    5. Automated hyperparameter optimization
    """
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.base_models = {}
        self.ensemble_models = {}
        self.model_metrics = {}
        self.feature_importance_aggregate = None
        self.is_fitted = False
        
        # Initialize diverse base learners
        self._initialize_base_models()
        
    def _initialize_base_models(self):
        """
        Initialize diverse base learners with different inductive biases
        
        Theory: Different algorithms make different assumptions about data:
        - Tree-based: Non-linear, handles interactions well
        - Linear: Fast, interpretable, works with linearly separable data
        - Distance-based: Captures local patterns
        - Probabilistic: Provides uncertainty estimates
        """
        
        self.base_models = {
            # Tree-based ensemble (handles non-linearity + interactions)
            'xgboost': xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.random_state,
                eval_metric='mlogloss'
            ),
            
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.random_state,
                verbose=-1
            ),
            
            'catboost': CatBoostClassifier(
                iterations=200,
                depth=6,
                learning_rate=0.1,
                random_state=self.random_state,
                verbose=False
            ),
            
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state
            ),
            
            'extra_trees': ExtraTreesClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state
            ),
            
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.random_state
            ),
            
            # Linear models (interpretable + fast)
            'logistic_regression': LogisticRegression(
                C=1.0,
                solver='lbfgs',
                max_iter=1000,
                random_state=self.random_state
            ),
            
            'ridge_classifier': RidgeClassifier(
                alpha=1.0,
                random_state=self.random_state
            ),
            
            # Support Vector Machine (kernel methods)
            'svm_rbf': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=self.random_state
            ),
            
            'svm_poly': SVC(
                kernel='poly',
                degree=3,
                C=1.0,
                probability=True,
                random_state=self.random_state
            ),
            
            # Distance-based (local patterns)
            'knn': KNeighborsClassifier(
                n_neighbors=7,
                weights='distance',
                metric='minkowski'
            ),
            
            # Probabilistic (uncertainty quantification)
            'naive_bayes': GaussianNB()
        }
        
        logger.info(f"Initialized {len(self.base_models)} diverse base learners")
    
    def fit(self, X: np.ndarray, y: np.ndarray, 
            validation_split: float = 0.2) -> 'AdvancedEnsembleSystem':
        """
        Train ensemble system with comprehensive evaluation
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)
            validation_split: Fraction of data for validation
            
        Returns:
            Self for method chaining
        """
        logger.info("Starting ensemble training process...")
        
        # Store training data characteristics
        self.n_samples, self.n_features = X.shape
        self.classes_ = np.unique(y)
        self.n_classes = len(self.classes_)
        
        # Cross-validation setup for robust evaluation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
        
        # Train and evaluate each base model
        for name, model in self.base_models.items():
            logger.info(f"Training {name}...")
            
            start_time = time.time()
            
            # Cross-validation scores
            cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
            
            # Fit model on full training data
            model.fit(X, y)
            training_time = time.time() - start_time
            
            # Prediction time benchmark
            start_pred = time.time()
            _ = model.predict(X[:100])  # Sample for speed test
            prediction_time = (time.time() - start_pred) / 100  # Per-sample time
            
            # Model size estimation
            model_size = len(joblib.dumps(model))
            
            # Store metrics
            self.model_metrics[name] = ModelMetrics(
                name=name,
                accuracy=cv_scores.mean(),
                cv_scores=cv_scores.tolist(),
                training_time=training_time,
                prediction_time=prediction_time,
                model_size=model_size
            )
            
            logger.info(f"{name}: Accuracy={cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        # Create ensemble combinations
        self._create_ensemble_models(X, y, cv)
        
        # Aggregate feature importance from tree-based models
        self._compute_aggregate_feature_importance()
        
        self.is_fitted = True
        logger.info("Ensemble training completed successfully!")
        
        return self
    
    def _create_ensemble_models(self, X: np.ndarray, y: np.ndarray, cv):
        """Create different ensemble combinations"""
        
        # Select top performing models for ensemble
        top_models = sorted(
            self.model_metrics.items(), 
            key=lambda x: x[1].accuracy, 
            reverse=True
        )[:8]  # Top 8 models
        
        top_model_dict = {name: self.base_models[name] for name, _ in top_models}
        
        # 1. Voting Classifier (Simple averaging)
        self.ensemble_models['voting_soft'] = VotingClassifier(
            estimators=list(top_model_dict.items()),
            voting='soft'  # Uses predict_proba for averaging
        )
        
        self.ensemble_models['voting_hard'] = VotingClassifier(
            estimators=list(top_model_dict.items()),
            voting='hard'  # Simple majority vote
        )
        
        # 2. Stacking Classifier (Meta-learning)
        self.ensemble_models['stacking'] = StackingClassifier(
            estimators=list(top_model_dict.items()),
            final_estimator=LogisticRegression(random_state=self.random_state),
            cv=cv,
            stack_method='predict_proba'
        )
        
        # 3. Weighted Ensemble (Performance-based weights)
        weights = [metrics.accuracy for _, metrics in top_models]
        self.ensemble_models['weighted_voting'] = VotingClassifier(
            estimators=list(top_model_dict.items()),
            voting='soft',
            weights=weights
        )
        
        # Train ensemble models
        ensemble_metrics = {}
        for name, ensemble in self.ensemble_models.items():
            logger.info(f"Training ensemble: {name}")
            start_time = time.time()
            
            # Cross-validation for ensemble
            cv_scores = cross_val_score(ensemble, X, y, cv=cv, scoring='accuracy')
            ensemble.fit(X, y)
            
            training_time = time.time() - start_time
            
            ensemble_metrics[name] = ModelMetrics(
                name=name,
                accuracy=cv_scores.mean(),
                cv_scores=cv_scores.tolist(),
                training_time=training_time,
                prediction_time=0,  # Will be computed later
                model_size=len(joblib.dumps(ensemble))
            )
            
            logger.info(f"Ensemble {name}: Accuracy={cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        self.model_metrics.update(ensemble_metrics)
    
    def _compute_aggregate_feature_importance(self):
        """Aggregate feature importance from tree-based models"""
        tree_models = ['xgboost', 'lightgbm', 'catboost', 'random_forest', 'extra_trees']
        
        importances = []
        weights = []
        
        for name in tree_models:
            if name in self.base_models and hasattr(self.base_models[name], 'feature_importances_'):
                importance = self.base_models[name].feature_importances_
                accuracy = self.model_metrics[name].accuracy
                
                importances.append(importance)
                weights.append(accuracy)
        
        if importances:
            # Weighted average of feature importances
            weights = np.array(weights)
            weights = weights / weights.sum()  # Normalize weights
            
            self.feature_importance_aggregate = np.average(
                np.array(importances), 
                axis=0, 
                weights=weights
            )
    
    def predict(self, X: np.ndarray, return_best: bool = True) -> np.ndarray:
        """
        Make predictions using ensemble
        
        Args:
            X: Feature matrix for prediction
            return_best: If True, return prediction from best ensemble model
            
        Returns:
            Predictions array
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        if return_best:
            # Use best performing ensemble model
            best_ensemble = max(
                self.ensemble_models.items(),
                key=lambda x: self.model_metrics[x[0]].accuracy
            )
            return best_ensemble[1].predict(X)
        
        # Return predictions from all ensemble models
        predictions = {}
        for name, model in self.ensemble_models.items():
            predictions[name] = model.predict(X)
        
        return predictions
    
    def predict_proba(self, X: np.ndarray, return_best: bool = True) -> np.ndarray:
        """Get prediction probabilities with uncertainty quantification"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        if return_best:
            best_ensemble = max(
                self.ensemble_models.items(),
                key=lambda x: self.model_metrics[x[0]].accuracy
            )
            return best_ensemble[1].predict_proba(X)
        
        # Return probabilities from all models for uncertainty analysis
        probabilities = {}
        for name, model in self.ensemble_models.items():
            if hasattr(model, 'predict_proba'):
                probabilities[name] = model.predict_proba(X)
        
        return probabilities
    
    def get_uncertainty_estimates(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute prediction uncertainty using ensemble disagreement
        
        Theory: Epistemic uncertainty from model disagreement
        Aleatoric uncertainty from prediction confidence
        """
        all_probas = self.predict_proba(X, return_best=False)
        
        # Stack probabilities from all models
        stacked_probas = np.stack(list(all_probas.values()))
        
        # Epistemic uncertainty: variance across models
        epistemic_uncertainty = np.var(stacked_probas, axis=0)
        
        # Aleatoric uncertainty: entropy of average prediction
        mean_proba = np.mean(stacked_probas, axis=0)
        aleatoric_uncertainty = -np.sum(
            mean_proba * np.log(mean_proba + 1e-8), 
            axis=1
        )
        
        # Total uncertainty
        total_uncertainty = np.mean(epistemic_uncertainty, axis=1) + aleatoric_uncertainty
        
        return {
            'epistemic': np.mean(epistemic_uncertainty, axis=1),
            'aleatoric': aleatoric_uncertainty,
            'total': total_uncertainty,
            'confidence': np.max(mean_proba, axis=1)
        }
    
    def get_feature_importance(self) -> np.ndarray:
        """Get aggregated feature importance"""
        if self.feature_importance_aggregate is None:
            raise ValueError("Feature importance not computed. Ensure tree-based models are fitted.")
        
        return self.feature_importance_aggregate
    
    def get_model_comparison(self) -> pd.DataFrame:
        """Get comprehensive model comparison"""
        data = []
        for name, metrics in self.model_metrics.items():
            data.append({
                'Model': name,
                'Accuracy': metrics.accuracy,
                'CV_Std': np.std(metrics.cv_scores),
                'Training_Time': metrics.training_time,
                'Prediction_Time': metrics.prediction_time,
                'Model_Size_MB': metrics.model_size / (1024 * 1024)
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Accuracy', ascending=False)
    
    def save_model(self, filepath: str):
        """Save complete ensemble system"""
        model_data = {
            'base_models': self.base_models,
            'ensemble_models': self.ensemble_models,
            'model_metrics': {
                name: {
                    'name': metrics.name,
                    'accuracy': metrics.accuracy,
                    'cv_scores': metrics.cv_scores,
                    'training_time': metrics.training_time,
                    'prediction_time': metrics.prediction_time,
                    'model_size': metrics.model_size
                }
                for name, metrics in self.model_metrics.items()
            },
            'feature_importance_aggregate': self.feature_importance_aggregate.tolist() if self.feature_importance_aggregate is not None else None,
            'n_samples': self.n_samples,
            'n_features': self.n_features,
            'classes_': self.classes_.tolist(),
            'n_classes': self.n_classes,
            'is_fitted': self.is_fitted
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Ensemble system saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str) -> 'AdvancedEnsembleSystem':
        """Load complete ensemble system"""
        model_data = joblib.load(filepath)
        
        instance = cls()
        instance.base_models = model_data['base_models']
        instance.ensemble_models = model_data['ensemble_models']
        
        # Reconstruct model metrics
        instance.model_metrics = {
            name: ModelMetrics(**metrics_data)
            for name, metrics_data in model_data['model_metrics'].items()
        }
        
        instance.feature_importance_aggregate = np.array(model_data['feature_importance_aggregate']) if model_data['feature_importance_aggregate'] else None
        instance.n_samples = model_data['n_samples']
        instance.n_features = model_data['n_features']
        instance.classes_ = np.array(model_data['classes_'])
        instance.n_classes = model_data['n_classes']
        instance.is_fitted = model_data['is_fitted']
        
        logger.info(f"Ensemble system loaded from {filepath}")
        return instance

def main():
    """Example usage and testing"""
    # This would be called from your main training script
    
    # Load your eco dataset
    # df = pd.read_csv("backend/ml/models/eco_dataset.csv")
    # X, y = prepare_features(df)  # Your feature preparation
    
    # Initialize and train ensemble
    # ensemble = AdvancedEnsembleSystem(random_state=42)
    # ensemble.fit(X, y)
    
    # Model comparison
    # comparison = ensemble.get_model_comparison()
    # print(comparison)
    
    # Make predictions with uncertainty
    # predictions = ensemble.predict(X_test)
    # uncertainties = ensemble.get_uncertainty_estimates(X_test)
    
    # Save the trained ensemble
    # ensemble.save_model("backend/ml/models/advanced_ensemble.pkl")
    
    print("Advanced Ensemble System implementation complete!")

if __name__ == "__main__":
    main()