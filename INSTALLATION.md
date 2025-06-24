# 🚀 Advanced Eco-Score Prediction System - Installation Guide

## Overview

This guide provides comprehensive instructions for installing and setting up the Advanced Eco-Score Prediction System, a dissertation-level machine learning platform with advanced ensemble methods, explainable AI, and real-time monitoring capabilities.

## System Requirements

### Minimum Requirements
- **Python**: 3.8+ (Python 3.9+ recommended)
- **Node.js**: 16+ (for frontend development)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

### Recommended Development Environment
- **Python**: 3.11
- **Node.js**: 18+
- **npm**: 9+
- **Redis**: Latest stable (for caching)
- **Git**: Latest stable

## Quick Installation

### Option 1: Automated Installation (Recommended)

The system includes an automated dependency installer that handles all requirements:

```bash
# Clone the repository
git clone <repository-url>
cd DSP

# Run the automated installer
python install_dependencies.py
```

### Option 2: Manual Installation

If you prefer manual control or the automated installer fails:

#### Step 1: Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 2: Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend/website

# Install Node.js dependencies
npm install

# Build frontend (optional, for production)
npm run build
```

## Dependency Details

### Core Python Libraries

The system uses the following key libraries:

#### Machine Learning & Data Science
- **numpy**: Numerical computing foundation
- **pandas**: Data manipulation and analysis
- **scikit-learn**: Core machine learning algorithms
- **xgboost**: Gradient boosting framework
- **scipy**: Scientific computing utilities
- **joblib**: Parallel computing and model persistence

#### Advanced ML & Ensemble Methods
- **imbalanced-learn**: Handling imbalanced datasets
- **catboost**: Categorical feature boosting
- **lightgbm**: Lightweight gradient boosting

#### Explainable AI
- **shap**: SHapley Additive exPlanations
- **lime**: Local Interpretable Model-agnostic Explanations
- **eli5**: Model interpretation library

#### Web Framework & Real-time Communication
- **Flask**: Web application framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-SocketIO**: Real-time bidirectional communication
- **python-socketio**: Socket.IO server
- **eventlet**: Concurrent networking library

#### Caching & Performance
- **redis**: In-memory data structure store
- **diskcache**: Disk-based caching
- **memory-profiler**: Memory usage monitoring

#### Data Processing & Validation
- **pydantic**: Data validation using Python type hints
- **marshmallow**: Object serialization/deserialization

#### Monitoring & Observability
- **prometheus-client**: Metrics collection
- **structlog**: Structured logging

#### Visualization
- **matplotlib**: Static plotting
- **seaborn**: Statistical data visualization
- **plotly**: Interactive visualizations

### Frontend Libraries

#### Core React Ecosystem
- **react**: UI library
- **react-dom**: DOM rendering
- **react-router-dom**: Client-side routing
- **@vitejs/plugin-react**: Vite React plugin

#### UI Components & Styling
- **@chakra-ui/react**: Component library
- **@emotion/react**: CSS-in-JS library
- **framer-motion**: Animation library
- **tailwindcss**: Utility-first CSS framework
- **@headlessui/react**: Unstyled UI components

#### Data Visualization
- **recharts**: React chart library
- **react-chartjs-2**: Chart.js wrapper
- **d3**: Data visualization library
- **plotly.js**: Interactive plotting
- **react-plotly.js**: Plotly React wrapper

#### State Management & Data Fetching
- **react-query**: Data fetching and caching
- **@tanstack/react-query**: Updated React Query
- **axios**: HTTP client

#### Real-time Communication
- **socket.io-client**: Socket.IO client

#### Form Handling & Validation
- **react-hook-form**: Form management
- **@hookform/resolvers**: Form validation resolvers
- **zod**: TypeScript-first schema validation

#### Utilities
- **lodash**: Utility library
- **date-fns**: Date manipulation
- **use-debounce**: Debouncing hook
- **react-error-boundary**: Error boundary component

## Installation Verification

### Backend Verification

Test your Python installation:

```python
# Test critical imports
python -c "
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
import flask
import shap
import lime
print('✅ All critical Python packages imported successfully!')
"
```

### Frontend Verification

Test your Node.js installation:

```bash
# Check versions
node --version
npm --version

# Test React development server
cd frontend/website
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_BASE_URL=http://localhost:5000

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:5000
```

### Redis Setup (Optional but Recommended)

For caching and real-time features:

#### Windows (using chocolatey):
```bash
choco install redis-64
redis-server
```

#### macOS (using homebrew):
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

## Running the System

### Development Mode

#### Start Backend:
```bash
cd backend
python -m flask run
# or
python app.py
```

#### Start Frontend:
```bash
cd frontend/website
npm run dev
```

#### Access the Application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- API Health Check: http://localhost:5000/api/health

### Production Deployment

For production deployment:

```bash
# Run the automated deployment script
python deploy_advanced_system.py
```

## Troubleshooting

### Common Issues

#### 1. Python Package Installation Failures

**Problem**: Packages fail to install due to compilation errors.

**Solutions**:
- Ensure you have Python development headers: `sudo apt-get install python3-dev` (Ubuntu)
- On Windows, install Microsoft C++ Build Tools
- Use conda instead of pip for problematic packages: `conda install <package>`

#### 2. Node.js Version Compatibility

**Problem**: npm install fails due to Node.js version mismatch.

**Solutions**:
- Use Node Version Manager (nvm): `nvm use 18`
- Update Node.js to latest LTS version
- Clear npm cache: `npm cache clean --force`

#### 3. Redis Connection Issues

**Problem**: Backend fails to connect to Redis.

**Solutions**:
- Ensure Redis is running: `redis-cli ping`
- Check Redis configuration in `.env` file
- Use Redis Docker container: `docker run -d -p 6379:6379 redis:alpine`

#### 4. Port Conflicts

**Problem**: Default ports (5000, 5173) are already in use.

**Solutions**:
- Change ports in configuration files
- Kill processes using the ports: `lsof -ti:5000 | xargs kill -9`

#### 5. Memory Issues

**Problem**: System runs out of memory during model training.

**Solutions**:
- Increase virtual memory/swap space
- Reduce dataset size for initial testing
- Use cloud computing resources for large-scale training

### Getting Help

1. **Check the Logs**: Both backend and frontend provide detailed logging
2. **Verify Installation**: Run `python install_dependencies.py --verify` for health check
3. **System Requirements**: Ensure your system meets minimum requirements
4. **Documentation**: Refer to component-specific documentation in respective directories

## Development Setup

### IDE Configuration

#### VS Code (Recommended)
Install these extensions:
- Python (Microsoft)
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Prettier - Code formatter
- GitLens

#### PyCharm/WebStorm
Configure interpreters for both Python and Node.js environments.

### Testing

#### Backend Tests:
```bash
cd backend
pytest tests/ -v
```

#### Frontend Tests:
```bash
cd frontend/website
npm test
```

### Code Quality

#### Python Code Formatting:
```bash
black backend/
flake8 backend/
mypy backend/
```

#### JavaScript Code Formatting:
```bash
cd frontend/website
npm run lint
npm run format
```

## Advanced Configuration

### Model Customization

To use custom models:

1. Place your trained models in `backend/ml/models/`
2. Update model paths in configuration files
3. Ensure feature names match your dataset

### Performance Tuning

#### Backend Performance:
- Configure Redis for optimal caching
- Adjust thread pool sizes in configuration
- Enable model prediction batching

#### Frontend Performance:
- Enable React Query caching
- Implement lazy loading for components
- Optimize bundle size with tree shaking

### Monitoring Setup

The system includes comprehensive monitoring:

1. **Prometheus Metrics**: Available at `/metrics` endpoint
2. **Health Checks**: Available at `/api/health`
3. **Real-time Dashboard**: Accessible through the web interface

## Next Steps

After successful installation:

1. **Load Sample Data**: Import your eco-score dataset
2. **Train Models**: Use the ensemble training pipeline
3. **Configure Monitoring**: Set up alerting and dashboards
4. **Deploy to Production**: Use the deployment scripts for cloud deployment

## Support

For technical support or questions:

1. Check this documentation thoroughly
2. Review the codebase comments and docstrings
3. Examine the example configurations provided
4. Refer to individual component documentation

---

**Installation Complete!** 🎉

Your Advanced Eco-Score Prediction System is now ready for use. The system provides a comprehensive, production-ready platform for eco-score prediction with advanced machine learning capabilities, real-time monitoring, and explainable AI features.