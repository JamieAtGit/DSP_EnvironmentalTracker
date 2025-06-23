# System Testing Framework

## Overview
System testing validates the complete integrated system to ensure it meets specified requirements and functions correctly in its intended environment.

## End-to-End Testing

### 1. Complete User Journey Testing

#### Scenario 1: Browser Extension Usage
```
Test Case: Carbon Footprint Display on Amazon Product Page
Preconditions: Extension installed and authenticated
Steps:
1. Navigate to Amazon product page
2. Wait for extension to analyze product
3. Verify carbon footprint tooltip appears
4. Click on tooltip for detailed information
5. Verify prediction accuracy and confidence level
6. Test feedback submission mechanism

Expected Results:
- Carbon footprint displayed within 3 seconds
- Tooltip integrates seamlessly with page design
- Prediction values within expected ranges
- Feedback mechanism functions correctly
```

#### Scenario 2: Web Application Workflow
```
Test Case: Manual Product Analysis
Preconditions: User logged into web application
Steps:
1. Access prediction form
2. Enter product details (name, material, weight, origin)
3. Submit prediction request
4. Review detailed carbon footprint analysis
5. Export results to CSV/PDF
6. Save product to personal dashboard

Expected Results:
- Form validation works correctly
- Prediction generates within 2 seconds
- Results page displays comprehensive analysis
- Export functionality produces valid files
- Dashboard updates with saved products
```

### 2. Data Flow Integration Testing

#### Complete ML Pipeline Test
```python
def test_complete_ml_pipeline():
    """Test entire ML pipeline from data input to prediction output."""
    
    # 1. Data Ingestion
    raw_product = {
        'name': 'Wireless Bluetooth Headphones',
        'brand': 'Sony',
        'weight': '250g',
        'material': 'plastic and metal',
        'origin': 'China'
    }
    
    # 2. Data Processing
    processed_data = preprocess_product_data(raw_product)
    assert validate_processed_data(processed_data)
    
    # 3. Feature Engineering
    features = extract_features(processed_data)
    assert features.shape[1] == EXPECTED_FEATURE_COUNT
    
    # 4. Model Prediction
    prediction = predict_carbon_footprint(features)
    assert prediction['carbon_footprint'] > 0
    assert 0 <= prediction['confidence'] <= 1
    
    # 5. Result Formatting
    formatted_result = format_prediction_result(prediction)
    assert all(key in formatted_result for key in REQUIRED_OUTPUT_FIELDS)
```

## Integration Testing

### 1. API Integration Testing

#### Backend Service Integration
```python
class TestAPIIntegration:
    def test_authentication_flow(self):
        """Test complete authentication workflow."""
        # Registration
        register_response = self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        })
        assert register_response.status_code == 201
        
        # Login
        login_response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'securepassword123'
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['access_token']
        
        # Authenticated request
        headers = {'Authorization': f'Bearer {token}'}
        protected_response = self.client.get('/api/profile', headers=headers)
        assert protected_response.status_code == 200
    
    def test_prediction_api_integration(self):
        """Test prediction API with real model."""
        product_data = {
            'name': 'Eco-friendly Water Bottle',
            'material': 'stainless steel',
            'weight': 0.4,
            'origin': 'Germany',
            'brand': 'EcoBottle'
        }
        
        response = self.client.post('/api/predict', json=product_data)
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Validate response structure
        assert 'carbon_footprint' in result
        assert 'confidence' in result
        assert 'breakdown' in result
        
        # Validate data types and ranges
        assert isinstance(result['carbon_footprint'], (int, float))
        assert result['carbon_footprint'] > 0
        assert 0 <= result['confidence'] <= 1
```

### 2. Database Integration Testing

#### Data Persistence Testing
```python
class TestDatabaseIntegration:
    def test_prediction_logging(self):
        """Test that predictions are properly logged to database."""
        product_data = self.sample_product_data
        
        # Make prediction
        response = self.client.post('/api/predict', json=product_data)
        prediction_id = response.get_json()['prediction_id']
        
        # Verify database entry
        logged_prediction = db.session.query(PredictionLog).filter_by(
            id=prediction_id
        ).first()
        
        assert logged_prediction is not None
        assert logged_prediction.carbon_footprint > 0
        assert logged_prediction.timestamp is not None
    
    def test_user_feedback_storage(self):
        """Test feedback mechanism and storage."""
        feedback_data = {
            'prediction_id': 'test_prediction_123',
            'user_rating': 4,
            'accuracy_feedback': 'good',
            'comments': 'Prediction seems reasonable'
        }
        
        response = self.client.post('/api/feedback', json=feedback_data)
        assert response.status_code == 201
        
        # Verify feedback stored
        feedback = db.session.query(UserFeedback).filter_by(
            prediction_id='test_prediction_123'
        ).first()
        
        assert feedback.user_rating == 4
        assert feedback.accuracy_feedback == 'good'
```

## Cross-Platform Testing

### 1. Browser Compatibility Testing

#### Extension Functionality Across Browsers
```javascript
// Selenium WebDriver Test
describe('Cross-Browser Extension Testing', () => {
    const browsers = ['chrome', 'firefox', 'edge'];
    
    browsers.forEach(browser => {
        describe(`${browser} compatibility`, () => {
            let driver;
            
            beforeEach(async () => {
                driver = await new Builder().forBrowser(browser).build();
                await loadExtension(driver, browser);
            });
            
            afterEach(async () => {
                await driver.quit();
            });
            
            test('extension loads correctly', async () => {
                await driver.get('https://amazon.com/product/test');
                
                // Wait for extension to initialize
                await driver.wait(until.elementLocated(
                    By.className('carbon-footprint-tooltip')
                ), 5000);
                
                const tooltip = await driver.findElement(
                    By.className('carbon-footprint-tooltip')
                );
                
                assert(await tooltip.isDisplayed());
            });
            
            test('popup functionality works', async () => {
                await openExtensionPopup(driver);
                
                const predictButton = await driver.findElement(
                    By.id('predict-button')
                );
                
                assert(await predictButton.isEnabled());
                
                await predictButton.click();
                
                await driver.wait(until.elementLocated(
                    By.className('prediction-result')
                ), 3000);
            });
        });
    });
});
```

### 2. Operating System Compatibility

#### Desktop Application Testing
```python
class TestCrossPlatformCompatibility:
    @pytest.mark.parametrize("platform", ["windows", "macos", "linux"])
    def test_backend_compatibility(self, platform):
        """Test backend runs correctly on different platforms."""
        if sys.platform != platform:
            pytest.skip(f"Not running on {platform}")
        
        # Test file path handling
        config_path = get_config_path()
        assert os.path.exists(config_path)
        
        # Test ML model loading
        model = load_model()
        assert model is not None
        
        # Test prediction functionality
        prediction = model.predict(self.sample_features)
        assert prediction is not None
```

## Performance System Testing

### 1. Load Testing

#### Concurrent User Testing
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def simulate_user_request(session, user_id):
    """Simulate a single user making a prediction request."""
    product_data = {
        'name': f'Test Product {user_id}',
        'material': 'plastic',
        'weight': 0.5,
        'origin': 'China'
    }
    
    async with session.post('/api/predict', json=product_data) as response:
        result = await response.json()
        return {
            'user_id': user_id,
            'status_code': response.status,
            'response_time': response.headers.get('X-Response-Time'),
            'carbon_footprint': result.get('carbon_footprint')
        }

async def load_test(num_users=100):
    """Test system with multiple concurrent users."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            simulate_user_request(session, i) 
            for i in range(num_users)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyze results
        successful_requests = sum(1 for r in results if r['status_code'] == 200)
        average_response_time = sum(
            float(r['response_time']) for r in results if r['response_time']
        ) / len(results)
        
        assert successful_requests >= num_users * 0.95  # 95% success rate
        assert average_response_time < 2.0  # Under 2 seconds average
        assert end_time - start_time < 30  # Complete within 30 seconds
```

### 2. Stress Testing

#### System Breaking Point Analysis
```python
def test_system_stress_limits():
    """Test system behavior under extreme load."""
    
    # Gradually increase load until failure
    for user_count in [50, 100, 200, 500, 1000]:
        try:
            results = run_load_test(user_count)
            
            success_rate = calculate_success_rate(results)
            avg_response_time = calculate_avg_response_time(results)
            
            logger.info(f"Users: {user_count}, Success: {success_rate:.2%}, "
                       f"Avg Response: {avg_response_time:.2f}s")
            
            # Define failure criteria
            if success_rate < 0.8 or avg_response_time > 5.0:
                logger.warning(f"System degradation at {user_count} users")
                break
                
        except Exception as e:
            logger.error(f"System failure at {user_count} users: {e}")
            break
```

## Environment Testing

### 1. Development Environment Testing
```bash
#!/bin/bash
# test_dev_environment.sh

echo "Testing Development Environment..."

# Check Python dependencies
python -c "import xgboost, pandas, numpy, flask" || exit 1

# Check Node.js dependencies
npm list react react-dom || exit 1

# Test database connectivity
python -c "from backend.models import db; db.engine.execute('SELECT 1')" || exit 1

# Test ML model loading
python -c "from backend.ml.models import load_model; load_model()" || exit 1

# Run basic functionality tests
pytest tests/integration/test_basic_functionality.py || exit 1

echo "Development environment tests passed!"
```

### 2. Production Environment Testing
```python
class TestProductionEnvironment:
    def test_ssl_configuration(self):
        """Test HTTPS configuration in production."""
        response = requests.get('https://api.carbontracker.com/health')
        assert response.status_code == 200
        assert response.url.startswith('https://')
    
    def test_environment_variables(self):
        """Test all required environment variables are set."""
        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'ML_MODEL_PATH',
            'REDIS_URL'
        ]
        
        for var in required_vars:
            assert os.getenv(var) is not None, f"Missing {var}"
    
    def test_monitoring_endpoints(self):
        """Test health check and monitoring endpoints."""
        health_response = requests.get('/health')
        assert health_response.status_code == 200
        assert health_response.json()['status'] == 'healthy'
        
        metrics_response = requests.get('/metrics')
        assert metrics_response.status_code == 200
```

## System Recovery Testing

### 1. Failure Recovery Testing
```python
def test_database_connection_recovery():
    """Test system recovery after database failure."""
    
    # Simulate database disconnection
    with mock.patch('backend.models.db.session') as mock_session:
        mock_session.side_effect = ConnectionError("Database unavailable")
        
        # System should handle gracefully
        response = client.post('/api/predict', json=sample_product_data)
        assert response.status_code == 503  # Service Unavailable
        assert 'temporarily unavailable' in response.get_json()['error']
    
    # Test recovery when database comes back online
    response = client.post('/api/predict', json=sample_product_data)
    assert response.status_code == 200

def test_ml_model_fallback():
    """Test fallback when ML model fails."""
    
    with mock.patch('backend.ml.predict_xgboost.load_model') as mock_load:
        mock_load.side_effect = FileNotFoundError("Model file not found")
        
        # Should fall back to rule-based system
        response = client.post('/api/predict', json=sample_product_data)
        assert response.status_code == 200
        
        result = response.get_json()
        assert result['method'] == 'rule_based'
        assert 'carbon_footprint' in result
```

## Test Execution Schedule

### 1. Continuous Integration
- **Every Commit**: Unit tests, lint checks
- **Pull Requests**: Integration tests, security scans
- **Daily**: Full system test suite
- **Weekly**: Performance and load testing

### 2. Release Testing
- **Pre-release**: Complete system test suite
- **Staging**: End-to-end user journey testing
- **Production**: Smoke tests and monitoring validation

## Test Reporting

### 1. Test Metrics Dashboard
```python
# Generate test report
def generate_test_report():
    return {
        'total_tests': count_total_tests(),
        'passed_tests': count_passed_tests(),
        'failed_tests': count_failed_tests(),
        'coverage_percentage': calculate_coverage(),
        'performance_metrics': {
            'avg_response_time': get_avg_response_time(),
            'throughput': get_throughput(),
            'error_rate': get_error_rate()
        },
        'security_scan_results': get_security_results(),
        'environment_health': check_environment_health()
    }
```

### 2. Automated Reporting
- Daily test summary emails
- Real-time dashboard updates
- Slack notifications for failures
- Weekly performance trend analysis