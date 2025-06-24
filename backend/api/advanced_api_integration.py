#!/usr/bin/env python3
"""
🔗 Advanced API Integration Layer
===============================

Theoretical Foundation:
- RESTful API Design: Stateless, cacheable, uniform interface
- WebSocket Protocol: Full-duplex communication for real-time updates
- Circuit Breaker Pattern: Fault tolerance for external dependencies
- Rate Limiting: Token bucket algorithm for API protection
- Event-Driven Architecture: Asynchronous message processing

Architecture:
- Flask + SocketIO for real-time communication
- Redis for session management and caching
- Celery for background task processing
- Circuit breakers for resilience
- Comprehensive monitoring and metrics
"""

from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import redis
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import concurrent.futures
from functools import wraps
import threading
from collections import defaultdict, deque
import uuid
import pickle

# Import our advanced ML components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ml.ensemble.advanced_ensemble_system import AdvancedEnsembleSystem
from ml.explainability.explainable_ai_engine import ExplainableAIEngine
from cache.intelligent_cache_system import IntelligentCacheSystem
from ml.adaptive.concept_drift_detection import ConceptDriftMonitor, AdaptiveLearningSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """API performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    current_connections: int = 0
    cache_hit_rate: float = 0.0
    model_predictions: int = 0
    explanations_generated: int = 0

class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance
    
    States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing)
    """
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

class RateLimiter:
    """
    Token bucket rate limiter
    
    Theory: Token bucket algorithm for smooth rate limiting
    """
    
    def __init__(self, capacity: int = 100, refill_rate: float = 10.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Attempt to acquire tokens"""
        with self.lock:
            now = time.time()
            
            # Refill tokens
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now
            
            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False

class AdvancedAPIIntegration:
    """
    Advanced API integration layer with real-time capabilities
    
    Features:
    1. Real-time WebSocket communication
    2. Circuit breaker pattern for resilience
    3. Intelligent caching integration
    4. Rate limiting and security
    5. Comprehensive monitoring
    6. Background task processing
    """
    
    def __init__(self, app: Flask, redis_url: str = "redis://localhost:6379"):
        self.app = app
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        # Initialize Redis for session management
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # Initialize advanced components
        self.cache_system = IntelligentCacheSystem(redis_url=redis_url)
        self.ensemble_model = None
        self.explainability_engine = None
        self.drift_monitor = None
        
        # Circuit breakers for external dependencies
        self.circuit_breakers = {
            'model_prediction': CircuitBreaker(failure_threshold=3, recovery_timeout=30),
            'explanation_generation': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
            'cache_operations': CircuitBreaker(failure_threshold=10, recovery_timeout=15)
        }
        
        # Rate limiting
        self.rate_limiters = {
            'prediction': RateLimiter(capacity=1000, refill_rate=50.0),  # 50 req/sec
            'explanation': RateLimiter(capacity=100, refill_rate=5.0),   # 5 req/sec
            'websocket': RateLimiter(capacity=500, refill_rate=25.0)     # 25 msg/sec
        }
        
        # Performance monitoring
        self.metrics = APIMetrics()
        self.request_history = deque(maxlen=1000)
        self.active_connections = set()
        
        # Background task executor
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # Initialize API routes and WebSocket handlers
        self._initialize_routes()
        self._initialize_websocket_handlers()
        
        logger.info("Advanced API Integration initialized")
    
    def load_models(self, 
                   ensemble_model_path: str,
                   feature_names: List[str],
                   class_names: List[str],
                   training_data: Any = None):
        """Load ML models and initialize engines"""
        try:
            # Load ensemble model
            self.ensemble_model = AdvancedEnsembleSystem.load_model(ensemble_model_path)
            logger.info("Ensemble model loaded successfully")
            
            # Initialize explainability engine
            if training_data is not None:
                self.explainability_engine = ExplainableAIEngine(
                    model=self.ensemble_model,
                    feature_names=feature_names,
                    class_names=class_names,
                    training_data=training_data
                )
                logger.info("Explainability engine initialized")
            
            # Initialize drift monitor
            self.drift_monitor = ConceptDriftMonitor(
                feature_names=feature_names,
                class_names=class_names
            )
            logger.info("Drift monitor initialized")
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    def _initialize_routes(self):
        """Initialize REST API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Comprehensive health check"""
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'ensemble_model': self.ensemble_model is not None,
                    'explainability_engine': self.explainability_engine is not None,
                    'drift_monitor': self.drift_monitor is not None,
                    'redis_cache': self.redis_client is not None,
                    'circuit_breakers': {
                        name: cb.state for name, cb in self.circuit_breakers.items()
                    }
                },
                'metrics': asdict(self.metrics),
                'cache_stats': self.cache_system.get_performance_stats() if self.cache_system else None
            }
            
            # Determine overall health
            if not all(health_status['components'].values()):
                health_status['status'] = 'degraded'\n            \n            return jsonify(health_status)\n        \n        @self.app.route('/api/predict-advanced', methods=['POST'])\n        def predict_advanced():\n            \"\"\"Advanced prediction with ensemble model\"\"\"\n            if not self.rate_limiters['prediction'].acquire():\n                return jsonify({'error': 'Rate limit exceeded'}), 429\n            \n            start_time = time.time()\n            request_id = str(uuid.uuid4())\n            \n            try:\n                data = request.get_json()\n                if not data or 'features' not in data:\n                    return jsonify({'error': 'Invalid request format'}), 400\n                \n                features = data['features']\n                include_uncertainty = data.get('include_uncertainty', True)\n                \n                # Use circuit breaker for model prediction\n                def make_prediction():\n                    if self.ensemble_model is None:\n                        raise Exception(\"Ensemble model not loaded\")\n                    \n                    # Convert features to numpy array\n                    import numpy as np\n                    feature_array = np.array(list(features.values())).reshape(1, -1)\n                    \n                    # Get predictions and probabilities\n                    prediction = self.ensemble_model.predict(feature_array)[0]\n                    probabilities = self.ensemble_model.predict_proba(feature_array)[0]\n                    \n                    result = {\n                        'prediction': prediction,\n                        'probabilities': probabilities.tolist(),\n                        'confidence': float(probabilities.max())\n                    }\n                    \n                    # Add uncertainty estimates if requested\n                    if include_uncertainty:\n                        uncertainty = self.ensemble_model.get_uncertainty_estimates(feature_array)\n                        result['uncertainty'] = {\n                            'epistemic': float(uncertainty['epistemic'][0]),\n                            'aleatoric': float(uncertainty['aleatoric'][0]),\n                            'total': float(uncertainty['total'][0])\n                        }\n                    \n                    return result\n                \n                # Execute with circuit breaker protection\n                prediction_result = self.circuit_breakers['model_prediction'].call(make_prediction)\n                \n                # Add metadata\n                prediction_result.update({\n                    'request_id': request_id,\n                    'timestamp': datetime.now().isoformat(),\n                    'response_time': time.time() - start_time,\n                    'model_version': getattr(self.ensemble_model, 'current_model_version', 'unknown')\n                })\n                \n                # Update metrics\n                self.metrics.successful_requests += 1\n                self.metrics.model_predictions += 1\n                \n                # Cache result\n                if self.cache_system:\n                    cache_key = self.cache_system._generate_cache_key(features, 'pred_adv')\n                    self.cache_system.put(cache_key, prediction_result, ttl=1800)\n                \n                # Emit real-time update\n                self.socketio.emit('prediction_update', prediction_result, namespace='/realtime')\n                \n                return jsonify(prediction_result)\n                \n            except Exception as e:\n                self.metrics.failed_requests += 1\n                logger.error(f\"Prediction failed: {e}\")\n                return jsonify({\n                    'error': 'Prediction failed',\n                    'request_id': request_id,\n                    'timestamp': datetime.now().isoformat()\n                }), 500\n            \n            finally:\n                # Update metrics\n                response_time = time.time() - start_time\n                self.metrics.total_requests += 1\n                \n                # Update moving average response time\n                alpha = 0.1\n                self.metrics.avg_response_time = (\n                    (1 - alpha) * self.metrics.avg_response_time + \n                    alpha * response_time\n                )\n                \n                # Store request history\n                self.request_history.append({\n                    'request_id': request_id,\n                    'endpoint': '/api/predict-advanced',\n                    'response_time': response_time,\n                    'timestamp': datetime.now().isoformat(),\n                    'status': 'success' if 'error' not in locals() else 'error'\n                })\n        \n        @self.app.route('/api/explain-advanced', methods=['POST'])\n        def explain_advanced():\n            \"\"\"Advanced explanation with multiple methods\"\"\"\n            if not self.rate_limiters['explanation'].acquire():\n                return jsonify({'error': 'Rate limit exceeded'}), 429\n            \n            start_time = time.time()\n            request_id = str(uuid.uuid4())\n            \n            try:\n                data = request.get_json()\n                if not data or 'features' not in data:\n                    return jsonify({'error': 'Invalid request format'}), 400\n                \n                features = data['features']\n                include_counterfactuals = data.get('include_counterfactuals', True)\n                include_uncertainty = data.get('include_uncertainty', True)\n                \n                # Use circuit breaker for explanation generation\n                def generate_explanation():\n                    if self.explainability_engine is None:\n                        raise Exception(\"Explainability engine not loaded\")\n                    \n                    import numpy as np\n                    feature_array = np.array(list(features.values()))\n                    \n                    # Generate comprehensive explanation\n                    explanation_result = self.explainability_engine.explain_instance(\n                        feature_array,\n                        include_counterfactuals=include_counterfactuals,\n                        include_uncertainty=include_uncertainty\n                    )\n                    \n                    # Generate visualizations\n                    visualizations = self.explainability_engine.generate_visualization(\n                        explanation_result\n                    )\n                    \n                    return {\n                        'explanation': asdict(explanation_result),\n                        'visualizations': visualizations\n                    }\n                \n                # Execute with circuit breaker protection\n                explanation_data = self.circuit_breakers['explanation_generation'].call(\n                    generate_explanation\n                )\n                \n                # Add metadata\n                explanation_data.update({\n                    'request_id': request_id,\n                    'timestamp': datetime.now().isoformat(),\n                    'response_time': time.time() - start_time\n                })\n                \n                # Update metrics\n                self.metrics.successful_requests += 1\n                self.metrics.explanations_generated += 1\n                \n                # Emit real-time update\n                self.socketio.emit('explanation_update', explanation_data, namespace='/realtime')\n                \n                return jsonify(explanation_data)\n                \n            except Exception as e:\n                self.metrics.failed_requests += 1\n                logger.error(f\"Explanation generation failed: {e}\")\n                return jsonify({\n                    'error': 'Explanation generation failed',\n                    'request_id': request_id,\n                    'timestamp': datetime.now().isoformat()\n                }), 500\n        \n        @self.app.route('/api/drift-status', methods=['GET'])\n        def drift_status():\n            \"\"\"Get concept drift monitoring status\"\"\"\n            if self.drift_monitor is None:\n                return jsonify({'error': 'Drift monitor not initialized'}), 503\n            \n            try:\n                drift_summary = self.drift_monitor.get_drift_summary()\n                return jsonify({\n                    'drift_summary': drift_summary,\n                    'timestamp': datetime.now().isoformat()\n                })\n            except Exception as e:\n                logger.error(f\"Drift status failed: {e}\")\n                return jsonify({'error': 'Failed to get drift status'}), 500\n        \n        @self.app.route('/api/performance-metrics', methods=['GET'])\n        def performance_metrics():\n            \"\"\"Get comprehensive performance metrics\"\"\"\n            try:\n                cache_stats = self.cache_system.get_performance_stats() if self.cache_system else {}\n                \n                metrics = {\n                    'api_metrics': asdict(self.metrics),\n                    'cache_performance': cache_stats,\n                    'circuit_breaker_status': {\n                        name: {\n                            'state': cb.state,\n                            'failure_count': cb.failure_count\n                        } for name, cb in self.circuit_breakers.items()\n                    },\n                    'rate_limiter_status': {\n                        name: {\n                            'tokens_available': rl.tokens,\n                            'capacity': rl.capacity\n                        } for name, rl in self.rate_limiters.items()\n                    },\n                    'active_connections': len(self.active_connections),\n                    'recent_requests': list(self.request_history)[-10:],  # Last 10 requests\n                    'timestamp': datetime.now().isoformat()\n                }\n                \n                return jsonify(metrics)\n                \n            except Exception as e:\n                logger.error(f\"Performance metrics failed: {e}\")\n                return jsonify({'error': 'Failed to get performance metrics'}), 500\n    \n    def _initialize_websocket_handlers(self):\n        \"\"\"Initialize WebSocket event handlers\"\"\"\n        \n        @self.socketio.on('connect', namespace='/realtime')\n        def handle_connect():\n            \"\"\"Handle WebSocket connection\"\"\"\n            if not self.rate_limiters['websocket'].acquire():\n                return False  # Reject connection\n            \n            connection_id = str(uuid.uuid4())\n            session['connection_id'] = connection_id\n            self.active_connections.add(connection_id)\n            self.metrics.current_connections = len(self.active_connections)\n            \n            join_room('predictions')\n            join_room('explanations')\n            \n            emit('connected', {\n                'connection_id': connection_id,\n                'timestamp': datetime.now().isoformat(),\n                'available_rooms': ['predictions', 'explanations', 'monitoring']\n            })\n            \n            logger.info(f\"WebSocket connection established: {connection_id}\")\n        \n        @self.socketio.on('disconnect', namespace='/realtime')\n        def handle_disconnect():\n            \"\"\"Handle WebSocket disconnection\"\"\"\n            connection_id = session.get('connection_id')\n            if connection_id:\n                self.active_connections.discard(connection_id)\n                self.metrics.current_connections = len(self.active_connections)\n                logger.info(f\"WebSocket connection closed: {connection_id}\")\n        \n        @self.socketio.on('join_room', namespace='/realtime')\n        def handle_join_room(data):\n            \"\"\"Handle room joining\"\"\"\n            room = data.get('room')\n            if room in ['predictions', 'explanations', 'monitoring']:\n                join_room(room)\n                emit('room_joined', {\n                    'room': room,\n                    'timestamp': datetime.now().isoformat()\n                })\n        \n        @self.socketio.on('leave_room', namespace='/realtime')\n        def handle_leave_room(data):\n            \"\"\"Handle room leaving\"\"\"\n            room = data.get('room')\n            leave_room(room)\n            emit('room_left', {\n                'room': room,\n                'timestamp': datetime.now().isoformat()\n            })\n        \n        @self.socketio.on('request_explanation', namespace='/realtime')\n        def handle_explanation_request(data):\n            \"\"\"Handle real-time explanation request\"\"\"\n            if not self.rate_limiters['explanation'].acquire():\n                emit('error', {'message': 'Rate limit exceeded'})\n                return\n            \n            # Process explanation request in background\n            def process_explanation():\n                try:\n                    features = data.get('features')\n                    if not features:\n                        return\n                    \n                    # Generate explanation (simplified for real-time)\n                    if self.explainability_engine:\n                        import numpy as np\n                        feature_array = np.array(list(features.values()))\n                        \n                        explanation_result = self.explainability_engine.explain_instance(\n                            feature_array,\n                            include_counterfactuals=False,  # Skip for speed\n                            include_uncertainty=True\n                        )\n                        \n                        # Emit to client\n                        self.socketio.emit('explanation_ready', {\n                            'instance_id': data.get('instance_id'),\n                            'explanation': asdict(explanation_result),\n                            'timestamp': datetime.now().isoformat()\n                        }, namespace='/realtime', room='explanations')\n                        \n                except Exception as e:\n                    logger.error(f\"Real-time explanation failed: {e}\")\n                    self.socketio.emit('explanation_error', {\n                        'instance_id': data.get('instance_id'),\n                        'error': str(e),\n                        'timestamp': datetime.now().isoformat()\n                    }, namespace='/realtime')\n            \n            # Submit to background executor\n            self.executor.submit(process_explanation)\n        \n        @self.socketio.on('subscribe_monitoring', namespace='/realtime')\n        def handle_monitoring_subscription():\n            \"\"\"Handle monitoring data subscription\"\"\"\n            join_room('monitoring')\n            \n            # Send initial monitoring data\n            cache_stats = self.cache_system.get_performance_stats() if self.cache_system else {}\n            \n            emit('monitoring_data', {\n                'metrics': asdict(self.metrics),\n                'cache_stats': cache_stats,\n                'active_connections': len(self.active_connections),\n                'timestamp': datetime.now().isoformat()\n            })\n    \n    def start_background_monitoring(self):\n        \"\"\"Start background monitoring tasks\"\"\"\n        def monitoring_loop():\n            while True:\n                try:\n                    # Update cache statistics\n                    if self.cache_system:\n                        cache_stats = self.cache_system.get_performance_stats()\n                        self.metrics.cache_hit_rate = cache_stats['performance_stats']['overall']['hit_rate']\n                    \n                    # Emit monitoring updates\n                    self.socketio.emit('monitoring_update', {\n                        'metrics': asdict(self.metrics),\n                        'timestamp': datetime.now().isoformat()\n                    }, namespace='/realtime', room='monitoring')\n                    \n                    # Sleep for 5 seconds\n                    time.sleep(5)\n                    \n                except Exception as e:\n                    logger.error(f\"Monitoring loop error: {e}\")\n                    time.sleep(10)  # Wait longer on error\n        \n        # Start monitoring in background thread\n        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)\n        monitoring_thread.start()\n        logger.info(\"Background monitoring started\")\n    \n    def update_drift_monitoring(self, X, y=None, y_pred=None):\n        \"\"\"Update drift monitoring with new data\"\"\"\n        if self.drift_monitor:\n            try:\n                drift_result = self.drift_monitor.update(X, y, y_pred)\n                \n                # Emit drift alerts if detected\n                if drift_result.drift_detected:\n                    self.socketio.emit('drift_alert', {\n                        'drift_result': asdict(drift_result),\n                        'timestamp': datetime.now().isoformat()\n                    }, namespace='/realtime', room='monitoring')\n                    \n                return drift_result\n            except Exception as e:\n                logger.error(f\"Drift monitoring update failed: {e}\")\n                return None\n    \n    def shutdown(self):\n        \"\"\"Graceful shutdown\"\"\"\n        logger.info(\"Shutting down Advanced API Integration...\")\n        \n        # Shutdown executor\n        self.executor.shutdown(wait=True)\n        \n        # Close Redis connections\n        if self.redis_client:\n            self.redis_client.close()\n        \n        logger.info(\"Advanced API Integration shutdown complete\")\n\ndef create_advanced_api(app: Flask, \n                       redis_url: str = \"redis://localhost:6379\",\n                       ensemble_model_path: Optional[str] = None,\n                       feature_names: Optional[List[str]] = None,\n                       class_names: Optional[List[str]] = None,\n                       training_data: Optional[Any] = None) -> AdvancedAPIIntegration:\n    \"\"\"Factory function to create advanced API integration\"\"\"\n    \n    # Enable CORS\n    CORS(app, supports_credentials=True, origins=[\"*\"])\n    \n    # Create advanced API integration\n    api_integration = AdvancedAPIIntegration(app, redis_url)\n    \n    # Load models if provided\n    if ensemble_model_path and feature_names and class_names:\n        api_integration.load_models(\n            ensemble_model_path=ensemble_model_path,\n            feature_names=feature_names,\n            class_names=class_names,\n            training_data=training_data\n        )\n    \n    # Start background monitoring\n    api_integration.start_background_monitoring()\n    \n    return api_integration\n\ndef main():\n    \"\"\"Example usage\"\"\"\n    app = Flask(__name__)\n    app.config['SECRET_KEY'] = 'development-key'\n    \n    # Feature and class names for eco-score prediction\n    feature_names = [\n        'Material Type', 'Transport Mode', 'Recyclability', 'Origin Country',\n        'Weight (log)', 'Weight Category', 'Packaging Type', 'Size Category', \n        'Quality Level', 'Pack Size', 'Material Confidence'\n    ]\n    class_names = ['A+', 'A', 'B', 'C', 'D', 'E', 'F']\n    \n    # Create advanced API\n    api_integration = create_advanced_api(\n        app=app,\n        redis_url=\"redis://localhost:6379\",\n        # ensemble_model_path=\"backend/ml/models/advanced_ensemble.pkl\",\n        feature_names=feature_names,\n        class_names=class_names\n    )\n    \n    # Run the application\n    if __name__ == '__main__':\n        api_integration.socketio.run(\n            app, \n            host='0.0.0.0', \n            port=5000, \n            debug=True,\n            use_reloader=False  # Disable reloader for WebSocket compatibility\n        )\n\nif __name__ == \"__main__\":\n    main()