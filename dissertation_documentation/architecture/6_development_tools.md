# Development Tools and Environment

## Overview
This document outlines the comprehensive development tools, environments, and workflows used in the Carbon Footprint Tracking System. It serves as a guide for setting up development environments and understanding the toolchain.

## 1. Development Environment Setup

### 1.1 Core Development Tools

#### Version Control
```bash
# Git Configuration
git --version  # Requirement: Git 2.25+

# Repository setup
git clone https://github.com/organization/carbon-footprint-tracker
cd carbon-footprint-tracker
git config --local user.name "Developer Name"
git config --local user.email "developer@example.com"

# Recommended Git aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --decorate"
```

#### Code Editors and IDEs
```yaml
# Primary IDE: Visual Studio Code
recommended_extensions:
  - Python: ms-python.python
  - JavaScript/TypeScript: esbenp.prettier-vscode
  - Docker: ms-azuretools.vscode-docker
  - Git: eamodio.gitlens
  - Database: mtxr.sqltools
  - REST Client: humao.rest-client
  - Jupyter: ms-toolsai.jupyter

# Alternative IDEs
alternatives:
  - PyCharm Professional (Python development)
  - WebStorm (Frontend development)
  - Vim/Neovim (with language servers)
  - Sublime Text (lightweight editing)
```

### 1.2 Environment Management

#### Python Environment
```bash
# Python Version Management with pyenv
curl https://pyenv.run | bash
pyenv install 3.9.16
pyenv local 3.9.16

# Virtual Environment Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Dependencies Installation
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Node.js Environment
```bash
# Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18.17.0
nvm use 18.17.0

# Package Manager
npm install -g yarn  # or use npm
yarn install  # Install dependencies

# Development server
yarn dev  # Start development server
yarn build  # Production build
yarn test  # Run tests
```

## 2. Backend Development Tools

### 2.1 Python Development Stack

#### Core Framework and Libraries
```python
# requirements.txt - Core Dependencies
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.2
Flask-CORS==4.3.1
Flask-Migrate==4.0.4

# ML/Data Science
xgboost==1.7.6
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
joblib==1.3.1

# Database
psycopg2-binary==2.9.7
redis==4.6.0
SQLAlchemy==2.0.19

# Utilities
python-dotenv==1.0.0
requests==2.31.0
celery==5.3.1
gunicorn==21.2.0
```

#### Development Dependencies
```python
# requirements-dev.txt - Development Tools
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
black==23.7.0
isort==5.12.0
flake8==6.0.0
mypy==1.5.1
pre-commit==3.3.3
bandit==1.7.5
safety==2.3.5
```

#### Code Quality Tools Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-x', 'tests/']
```

### 2.2 Database Development Tools

#### Database Management
```bash
# PostgreSQL Setup (Docker)
docker run --name carbon-db \
  -e POSTGRES_DB=carbon_tracker \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Redis Setup (Docker)
docker run --name carbon-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Database Migration with Alembic
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### Database Tools
```bash
# CLI Tools
psql -h localhost -U postgres -d carbon_tracker
redis-cli -p 6379

# GUI Tools (Recommendations)
# - pgAdmin 4 (PostgreSQL)
# - DBeaver (Multi-database)
# - Redis Commander (Redis)
# - DataGrip (JetBrains)
```

## 3. Frontend Development Tools

### 3.1 Web Application Stack

#### Core Dependencies
```json
// package.json - Dependencies
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.2",
    "@reduxjs/toolkit": "^1.9.5",
    "react-redux": "^8.1.2",
    "axios": "^1.4.0",
    "@mui/material": "^5.14.5",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "recharts": "^2.7.2",
    "date-fns": "^2.30.0"
  }
}
```

#### Development Dependencies
```json
// package.json - DevDependencies
{
  "devDependencies": {
    "@types/react": "^18.2.20",
    "@types/react-dom": "^18.2.7",
    "@vitejs/plugin-react": "^4.0.4",
    "vite": "^4.4.8",
    "typescript": "^5.1.6",
    "eslint": "^8.47.0",
    "@typescript-eslint/eslint-plugin": "^6.4.0",
    "@typescript-eslint/parser": "^6.4.0",
    "prettier": "^3.0.2",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.0",
    "jest": "^29.6.2",
    "husky": "^8.0.3",
    "lint-staged": "^14.0.1"
  }
}
```

### 3.2 Browser Extension Development

#### Extension Manifest and Build Tools
```json
// manifest.json - Extension Configuration
{
  "manifest_version": 3,
  "name": "Carbon Footprint Tracker",
  "version": "1.0.0",
  "description": "Track carbon footprint of products while shopping",
  "permissions": [
    "activeTab",
    "storage",
    "scripting"
  ],
  "host_permissions": [
    "https://*.amazon.com/*",
    "https://*.amazon.co.uk/*"
  ],
  "content_scripts": [
    {
      "matches": ["https://*.amazon.com/*"],
      "js": ["content.js"],
      "css": ["styles.css"]
    }
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html",
    "default_title": "Carbon Footprint Tracker"
  }
}
```

#### Extension Build Configuration
```javascript
// vite.config.js - Extension Build
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'popup.html'),
        content: resolve(__dirname, 'src/content.js'),
        background: resolve(__dirname, 'src/background.js')
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify('production')
  }
});
```

## 4. Machine Learning Development Tools

### 4.1 ML Development Environment

#### Jupyter Notebook Setup
```bash
# Jupyter Installation
pip install jupyter jupyterlab ipykernel

# Kernel Setup
python -m ipykernel install --user --name carbon-ml --display-name "Carbon ML"

# Launch Jupyter
jupyter lab
# or
jupyter notebook
```

#### ML Libraries and Tools
```python
# ML-specific requirements
# requirements-ml.txt
jupyter==1.0.0
jupyterlab==4.0.5
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0
optuna==3.2.0
shap==0.42.1
mlflow==2.5.0
tensorboard==2.13.0
```

### 4.2 Model Development Workflow

#### Experiment Tracking
```python
# MLflow Setup
import mlflow
import mlflow.xgboost

# Start tracking
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("carbon-footprint-prediction")

# Log experiment
with mlflow.start_run():
    mlflow.log_param("max_depth", 6)
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", 0.85)
    mlflow.xgboost.log_model(model, "model")
```

#### Model Validation Framework
```python
# validation_framework.py
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
import joblib

class ModelValidator:
    def __init__(self, model, X_test, y_test):
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
    
    def validate_performance(self):
        # Cross-validation
        cv_scores = cross_val_score(self.model, self.X_test, self.y_test, cv=5)
        
        # Predictions
        y_pred = self.model.predict(self.X_test)
        
        # Classification report
        report = classification_report(self.y_test, y_pred)
        
        return {
            'cv_scores': cv_scores,
            'mean_cv_score': cv_scores.mean(),
            'classification_report': report
        }
```

## 5. DevOps and Deployment Tools

### 5.1 Containerization

#### Docker Configuration
```dockerfile
# Dockerfile - Backend Service
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```yaml
# docker-compose.yml - Development Environment
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/carbon_tracker
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=carbon_tracker
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 5.2 CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.9
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --statistics
    
    - name: Type check with mypy
      run: mypy backend/
    
    - name: Test with pytest
      run: |
        pytest --cov=backend tests/
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'yarn'
    
    - name: Install dependencies
      run: yarn install --frozen-lockfile
    
    - name: Lint
      run: yarn lint
    
    - name: Type check
      run: yarn type-check
    
    - name: Test
      run: yarn test --coverage
    
    - name: Build
      run: yarn build

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: 'security-scan-results.sarif'
```

## 6. Testing Tools and Frameworks

### 6.1 Backend Testing

#### Python Testing Stack
```python
# test_config.py
import pytest
from backend.app import create_app
from backend.models import db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Login and get JWT token
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
```

#### Testing Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=backend
    --cov-branch
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
```

### 6.2 Frontend Testing

#### JavaScript Testing Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
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

## 7. Monitoring and Observability Tools

### 7.1 Application Monitoring

#### Logging Configuration
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/carbon_tracker.log',
            maxBytes=10240000,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Carbon Tracker startup')
```

#### Metrics Collection
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
prediction_requests = Counter(
    'prediction_requests_total',
    'Total number of prediction requests'
)

prediction_duration = Histogram(
    'prediction_duration_seconds',
    'Time spent processing predictions'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        def new_start_response(status, response_headers):
            prediction_duration.observe(time.time() - start_time)
            if '/api/predict' in environ.get('PATH_INFO', ''):
                prediction_requests.inc()
            return start_response(status, response_headers)
        
        return self.app(environ, new_start_response)
```

## 8. Development Workflow

### 8.1 Branch Strategy
```bash
# Git Flow Workflow
git checkout -b feature/carbon-calculation-improvement
git commit -m "feat: improve carbon calculation accuracy"
git push origin feature/carbon-calculation-improvement

# Pull Request Process
# 1. Create PR against develop branch
# 2. Code review by 2+ team members
# 3. All tests must pass
# 4. Merge after approval
```

### 8.2 Code Standards
```yaml
# Development Standards
code_style:
  python: black + isort + flake8
  javascript: prettier + eslint
  commit_messages: conventional commits
  documentation: sphinx (python) + jsdoc (javascript)

code_review:
  required_reviewers: 2
  checks:
    - tests_pass
    - security_scan_pass
    - code_coverage: ">= 80%"
    - performance_impact: minimal
```

This comprehensive development tools documentation ensures consistent development practices and environments across the team, essential for maintaining code quality and productivity for a dissertation project at the University of the West of England Bristol.