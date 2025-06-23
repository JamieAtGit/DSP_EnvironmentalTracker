# Unit Testing Framework

## Overview
Unit testing validates individual components and functions in isolation to ensure they perform correctly according to their specifications.

## Testing Strategy

### 1. Test-Driven Development (TDD)
- **Red-Green-Refactor Cycle**
  - Write failing tests first
  - Implement minimal code to pass
  - Refactor while maintaining tests
  - Continuous integration with test suite

### 2. Test Isolation
- **Independent Test Execution**
  - No shared state between tests
  - Mock external dependencies
  - Database transactions rollback
  - Clean test environment setup

## Backend Unit Tests

### 1. Machine Learning Module Tests

#### Model Training (`backend/ml/training/`)
```python
# test_train_xgboost.py
class TestXGBoostTraining:
    def test_data_preprocessing(self):
        # Test data cleaning and feature engineering
        raw_data = load_test_dataset()
        processed_data = preprocess_data(raw_data)
        
        assert processed_data.shape[1] == EXPECTED_FEATURES
        assert not processed_data.isnull().any().any()
        assert all(col in processed_data.columns for col in REQUIRED_FEATURES)
    
    def test_model_training_pipeline(self):
        # Test complete training workflow
        X_train, X_test, y_train, y_test = prepare_test_data()
        model, metrics = train_xgboost_model(X_train, y_train, X_test, y_test)
        
        assert model is not None
        assert metrics['accuracy'] > 0.8
        assert metrics['f1_score'] > 0.75
        assert 'confusion_matrix' in metrics
    
    def test_feature_importance_extraction(self):
        # Test feature importance calculation
        model = load_trained_model()
        importance = get_feature_importance(model)
        
        assert len(importance) == EXPECTED_FEATURES
        assert sum(importance.values()) == pytest.approx(1.0, rel=1e-2)
```

#### Prediction Module (`backend/ml/prediction/`)
```python
# test_predict_xgboost.py
class TestXGBoostPrediction:
    @pytest.fixture
    def mock_model(self):
        return Mock(spec=xgb.XGBClassifier)
    
    @pytest.fixture
    def sample_product_data(self):
        return {
            'material': 'plastic',
            'weight': 0.5,
            'origin': 'China',
            'transport_method': 'air'
        }
    
    def test_single_prediction(self, mock_model, sample_product_data):
        # Test individual product prediction
        with patch('joblib.load', return_value=mock_model):
            mock_model.predict.return_value = [0.75]
            
            result = predict_carbon_footprint(sample_product_data)
            
            assert 'carbon_footprint' in result
            assert isinstance(result['carbon_footprint'], float)
            assert result['carbon_footprint'] >= 0
    
    def test_batch_prediction(self, mock_model):
        # Test multiple product predictions
        products = [self.sample_product_data] * 5
        
        with patch('joblib.load', return_value=mock_model):
            mock_model.predict.return_value = [0.1, 0.3, 0.5, 0.7, 0.9]
            
            results = batch_predict_carbon_footprint(products)
            
            assert len(results) == 5
            assert all('carbon_footprint' in result for result in results)
    
    def test_invalid_input_handling(self):
        # Test error handling for invalid inputs
        invalid_data = {'invalid_field': 'test'}
        
        with pytest.raises(ValidationError):
            predict_carbon_footprint(invalid_data)
```

### 2. API Layer Tests

#### Data Controller (`backend/api/controllers/`)
```python
# test_data_controller.py
class TestDataController:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        return app.test_client()
    
    def test_predict_endpoint_valid_data(self, client):
        # Test successful prediction request
        product_data = {
            'name': 'Test Product',
            'material': 'plastic',
            'weight': 0.5,
            'brand': 'TestBrand'
        }
        
        response = client.post('/api/predict', json=product_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'carbon_footprint' in data
        assert 'confidence' in data
        assert isinstance(data['carbon_footprint'], (int, float))
    
    def test_predict_endpoint_invalid_data(self, client):
        # Test validation error handling
        invalid_data = {'name': 'Test'}  # Missing required fields
        
        response = client.post('/api/predict', json=invalid_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validation' in data['error'].lower()
    
    def test_batch_predict_endpoint(self, client):
        # Test batch prediction functionality
        products = [
            {'name': 'Product 1', 'material': 'plastic', 'weight': 0.3},
            {'name': 'Product 2', 'material': 'metal', 'weight': 1.2}
        ]
        
        response = client.post('/api/batch_predict', json=products)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['predictions']) == 2
```

### 3. Data Processing Tests

#### Data Cleaning (`backend/data/processing/`)
```python
# test_clean_dataset.py
class TestDataCleaning:
    def test_remove_duplicates(self):
        # Test duplicate removal
        data = pd.DataFrame({
            'product_id': [1, 1, 2, 3, 3],
            'name': ['A', 'A', 'B', 'C', 'C']
        })
        
        cleaned = remove_duplicates(data)
        
        assert len(cleaned) == 3
        assert cleaned['product_id'].nunique() == 3
    
    def test_handle_missing_values(self):
        # Test missing value imputation
        data = pd.DataFrame({
            'weight': [1.0, None, 2.0, None, 3.0],
            'material': ['plastic', None, 'metal', 'plastic', None]
        })
        
        processed = handle_missing_values(data)
        
        assert not processed['weight'].isnull().any()
        assert not processed['material'].isnull().any()
    
    def test_standardize_units(self):
        # Test unit standardization
        data = pd.DataFrame({
            'weight': [1000, 500, 2000],  # grams
            'weight_unit': ['g', 'g', 'g']
        })
        
        standardized = standardize_weight_to_kg(data)
        
        assert standardized['weight'].tolist() == [1.0, 0.5, 2.0]
        assert all(unit == 'kg' for unit in standardized['weight_unit'])
```

## Frontend Unit Tests

### 1. React Component Tests

#### Browser Extension Components
```javascript
// test/components/ProductPage.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import ProductPage from '../src/components/ProductPage';

describe('ProductPage Component', () => {
    const mockProductData = {
        name: 'Test Product',
        material: 'plastic',
        carbonFootprint: 2.5,
        confidence: 0.85
    };

    test('renders product information correctly', () => {
        render(<ProductPage product={mockProductData} />);
        
        expect(screen.getByText('Test Product')).toBeInTheDocument();
        expect(screen.getByText('plastic')).toBeInTheDocument();
        expect(screen.getByText('2.5 kg CO₂')).toBeInTheDocument();
    });

    test('displays confidence level', () => {
        render(<ProductPage product={mockProductData} />);
        
        expect(screen.getByText('85% confidence')).toBeInTheDocument();
    });

    test('handles missing data gracefully', () => {
        const incompleteData = { name: 'Test Product' };
        render(<ProductPage product={incompleteData} />);
        
        expect(screen.getByText('Test Product')).toBeInTheDocument();
        expect(screen.getByText('Data not available')).toBeInTheDocument();
    });
});
```

#### API Service Tests
```javascript
// test/services/api.test.js
import api from '../src/services/api';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Service', () => {
    beforeEach(() => {
        fetch.mockClear();
    });

    test('predicts carbon footprint successfully', async () => {
        const mockResponse = {
            carbon_footprint: 2.5,
            confidence: 0.85,
            factors: { material: 'high', transport: 'medium' }
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockResponse
        });

        const productData = {
            name: 'Test Product',
            material: 'plastic',
            weight: 0.5
        };

        const result = await api.predictCarbonFootprint(productData);

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/predict'),
            expect.objectContaining({
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            })
        );

        expect(result).toEqual(mockResponse);
    });

    test('handles API errors appropriately', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 500,
            json: async () => ({ error: 'Internal server error' })
        });

        const productData = { name: 'Test Product' };

        await expect(api.predictCarbonFootprint(productData))
            .rejects.toThrow('API request failed');
    });
});
```

## Test Configuration & Setup

### 1. Python Test Configuration
```python
# conftest.py
import pytest
import tempfile
import os
from backend.api.app import create_app
from backend.ml.models import db

@pytest.fixture
def app():
    """Create application for testing."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        db.init_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def sample_dataset():
    """Sample dataset for testing."""
    return pd.DataFrame({
        'product_name': ['Product A', 'Product B'],
        'material': ['plastic', 'metal'],
        'weight': [0.5, 1.2],
        'origin': ['China', 'Germany'],
        'carbon_footprint': [2.1, 4.3]
    })
```

### 2. JavaScript Test Configuration
```javascript
// jest.config.js
module.exports = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
    moduleNameMapping: {
        '\\.(css|less|scss)$': 'identity-obj-proxy'
    },
    collectCoverageFrom: [
        'src/**/*.{js,jsx}',
        '!src/index.js',
        '!src/setupTests.js'
    ],
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    }
};
```

## Test Automation & CI/CD

### 1. GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=backend tests/
    
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: 16
    
    - name: Install dependencies
      run: npm install
    
    - name: Run tests
      run: npm test -- --coverage
```

## Coverage Requirements

### 1. Coverage Targets
- **Backend Python Code**: 90% line coverage
- **Frontend JavaScript Code**: 85% line coverage
- **Critical ML Functions**: 95% line coverage
- **API Endpoints**: 100% coverage

### 2. Coverage Reporting
```bash
# Python Coverage Report
pytest --cov=backend --cov-report=html --cov-report=term

# JavaScript Coverage Report
npm test -- --coverage --coverageReporters=html --coverageReporters=text
```