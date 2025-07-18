# Installation Instructions

## For macOS with Python 3.13 (your current setup):

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## For Python 3.9 or older systems:

1. Create a new virtual environment:
```bash
python3 -m venv venv_py39
source venv_py39/bin/activate
```

2. Install dependencies with Python 3.9 compatible versions:
```bash
pip install -r requirements_py39.txt
```

## Key version changes for Python 3.9 compatibility:
- pgeocode: 0.5.0 → 0.4.1
- numpy: 2.2.5 → 1.26.4
- matplotlib: 3.10.0 → 3.9.4
- xgboost: 3.0.0 → 2.1.3
- imbalanced-learn: 0.13.0 → 0.12.4

## To verify installation:
```bash
python -c "import xgboost; import sklearn; print('All packages installed successfully!')"
```