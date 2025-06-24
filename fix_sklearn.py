#!/usr/bin/env python3
"""
🔧 Scikit-learn Installation Fix
===============================

Fixes common scikit-learn import issues and ensures proper installation.
"""

import sys
import subprocess
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_sklearn():
    """Fix scikit-learn installation issues"""
    
    logger.info("🔧 Diagnosing scikit-learn installation...")
    
    # Test different import methods
    import_attempts = [
        ('sklearn', 'Standard sklearn import'),
        ('sklearn.ensemble', 'sklearn.ensemble import'),
        ('sklearn.linear_model', 'sklearn.linear_model import'),
        ('scikit-learn', 'Direct scikit-learn import'),
    ]
    
    working_imports = []
    failed_imports = []
    
    for module, description in import_attempts:
        try:
            importlib.import_module(module)
            logger.info(f"✅ {description} - SUCCESS")
            working_imports.append(module)
        except ImportError as e:
            logger.warning(f"❌ {description} - FAILED: {e}")
            failed_imports.append((module, str(e)))
    
    if 'sklearn' in working_imports:
        logger.info("✅ scikit-learn is working correctly!")
        return True
    
    logger.info("🔄 Attempting to fix scikit-learn...")
    
    # Fix attempt 1: Reinstall scikit-learn
    logger.info("Attempt 1: Reinstalling scikit-learn...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "uninstall", "scikit-learn", "-y"
        ], check=True, capture_output=True)
        
        subprocess.run([
            sys.executable, "-m", "pip", "install", "scikit-learn", "--no-cache-dir"
        ], check=True, capture_output=True)
        
        # Test import
        import sklearn
        logger.info("✅ Fix attempt 1 successful!")
        return True
        
    except Exception as e:
        logger.warning(f"Fix attempt 1 failed: {e}")
    
    # Fix attempt 2: Install specific version
    logger.info("Attempt 2: Installing specific scikit-learn version...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "scikit-learn==1.3.0", "--force-reinstall"
        ], check=True, capture_output=True)
        
        # Test import
        import sklearn
        logger.info("✅ Fix attempt 2 successful!")
        return True
        
    except Exception as e:
        logger.warning(f"Fix attempt 2 failed: {e}")
    
    # Fix attempt 3: Install with conda (if available)
    logger.info("Attempt 3: Trying conda installation...")
    try:
        subprocess.run([
            "conda", "install", "scikit-learn", "-y"
        ], check=True, capture_output=True)
        
        # Test import
        import sklearn
        logger.info("✅ Fix attempt 3 successful!")
        return True
        
    except Exception as e:
        logger.warning(f"Fix attempt 3 failed: {e}")
    
    # Fix attempt 4: Install dependencies first
    logger.info("Attempt 4: Installing dependencies first...")
    try:
        # Install dependencies
        dependencies = [
            "numpy>=1.17.3",
            "scipy>=1.3.2", 
            "joblib>=1.0.0",
            "threadpoolctl>=2.0.0"
        ]
        
        for dep in dependencies:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
        
        # Now install scikit-learn
        subprocess.run([
            sys.executable, "-m", "pip", "install", "scikit-learn", "--no-deps"
        ], check=True, capture_output=True)
        
        # Test import
        import sklearn
        logger.info("✅ Fix attempt 4 successful!")
        return True
        
    except Exception as e:
        logger.warning(f"Fix attempt 4 failed: {e}")
    
    logger.error("❌ All fix attempts failed. Manual intervention required.")
    
    print("""
🚨 Scikit-learn Installation Failed

Manual fixes to try:

1. Check Python version compatibility:
   python --version
   (scikit-learn requires Python 3.8+)

2. Clear pip cache and reinstall:
   pip cache purge
   pip install --no-cache-dir --force-reinstall scikit-learn

3. Use conda instead of pip:
   conda install scikit-learn

4. Install from source:
   pip install --no-use-pep517 scikit-learn

5. Check for conflicting packages:
   pip list | grep -i scikit

6. Update pip and setuptools:
   python -m pip install --upgrade pip setuptools wheel

7. Install in a clean virtual environment:
   python -m venv clean_env
   clean_env\\Scripts\\activate  # Windows
   source clean_env/bin/activate  # Linux/Mac
   pip install scikit-learn
    """)
    
    return False

if __name__ == "__main__":
    success = fix_sklearn()
    if success:
        print("🎉 Scikit-learn is now working correctly!")
    else:
        print("❌ Manual intervention required for scikit-learn")
        sys.exit(1)