#!/usr/bin/env python3
"""
🚀 Dependency Installation & Verification Script
===============================================

Comprehensive dependency management for the Advanced Eco-Score Prediction System.
Ensures all Python and JavaScript libraries are properly installed and verified.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class InstallationResult:
    """Installation result tracking"""
    component: str
    success: bool
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None

class DependencyManager:
    """
    Comprehensive dependency management system
    
    Features:
    1. Python package installation and verification
    2. Node.js package installation and verification
    3. System dependency checks
    4. Installation health verification
    5. Automated troubleshooting
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend" / "website"
        
        self.installation_results: List[InstallationResult] = []
        
        logger.info(f"Dependency Manager initialized for {self.project_root}")
    
    def install_all_dependencies(self) -> bool:
        """
        Install all dependencies for the entire system
        
        Returns:
            Success status
        """
        logger.info("🚀 Starting comprehensive dependency installation...")
        
        success = True
        
        # 1. Check system prerequisites
        success &= self._check_system_prerequisites()
        
        # 2. Install Python dependencies
        success &= self._install_python_dependencies()
        
        # 3. Install Node.js dependencies
        success &= self._install_nodejs_dependencies()
        
        # 4. Verify installations
        success &= self._verify_installations()
        
        # 5. Generate installation report
        self._generate_installation_report()
        
        if success:
            logger.info("✅ All dependencies installed successfully!")
            print("""
🎉 Installation Complete!

Your Advanced Eco-Score Prediction System is ready to run.
You can now start the system using:

Backend:  cd backend && python -m flask run
Frontend: cd frontend/website && npm run dev

For deployment: python deploy_advanced_system.py
            """)
        else:
            logger.error("❌ Some dependencies failed to install. Check the report above.")
        
        return success
    
    def _check_system_prerequisites(self) -> bool:
        """Check system prerequisites"""
        logger.info("🔍 Checking system prerequisites...")
        
        start_time = time.time()
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major != 3 or python_version.minor < 8:
                raise Exception(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            
            logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check pip
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("pip not available")
            
            logger.info(f"✅ {result.stdout.strip()}")
            
            # Check Node.js (if available)
            try:
                result = subprocess.run(["node", "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✅ Node.js {result.stdout.strip()}")
                else:
                    logger.warning("⚠️ Node.js not found - frontend features will be limited")
            except FileNotFoundError:
                logger.warning("⚠️ Node.js not found - frontend features will be limited")
            
            # Check npm (if available)
            try:
                result = subprocess.run(["npm", "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✅ npm {result.stdout.strip()}")
            except FileNotFoundError:
                logger.warning("⚠️ npm not found - frontend dependencies cannot be installed")
            
            self.installation_results.append(
                InstallationResult(
                    component="System Prerequisites",
                    success=True,
                    message="All system prerequisites verified",
                    duration=time.time() - start_time
                )
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System prerequisite check failed: {e}")
            
            self.installation_results.append(
                InstallationResult(
                    component="System Prerequisites",
                    success=False,
                    message=str(e),
                    duration=time.time() - start_time
                )
            )
            
            return False
    
    def _install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("🐍 Installing Python dependencies...")
        
        start_time = time.time()
        
        try:
            requirements_file = self.backend_dir / "requirements.txt"
            
            if not requirements_file.exists():
                raise Exception(f"Requirements file not found: {requirements_file}")
            
            # Upgrade pip first
            logger.info("Upgrading pip...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Pip upgrade warning: {result.stderr}")
            
            # Install requirements
            logger.info(f"Installing from {requirements_file}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pip install failed: {result.stderr}")
            
            logger.info("✅ Python dependencies installed successfully")
            
            # Count installed packages
            installed_packages = self._count_installed_python_packages()
            
            self.installation_results.append(
                InstallationResult(
                    component="Python Dependencies",
                    success=True,
                    message=f"Successfully installed {installed_packages} packages",
                    duration=time.time() - start_time,
                    details={"packages_count": installed_packages}
                )
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Python dependency installation failed: {e}")
            
            self.installation_results.append(
                InstallationResult(
                    component="Python Dependencies",
                    success=False,
                    message=str(e),
                    duration=time.time() - start_time
                )
            )
            
            return False
    
    def _install_nodejs_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        logger.info("🟩 Installing Node.js dependencies...")
        
        start_time = time.time()
        
        try:
            package_json = self.frontend_dir / "package.json"
            
            if not package_json.exists():
                logger.warning(f"⚠️ package.json not found: {package_json}")
                return True  # Not critical for backend-only operation
            
            # Check if npm is available
            try:
                subprocess.run(["npm", "--version"], capture_output=True, check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                logger.warning("⚠️ npm not available, skipping Node.js dependencies")
                return True  # Not critical for backend-only operation
            
            # Change to frontend directory and install
            original_dir = os.getcwd()
            os.chdir(self.frontend_dir)
            
            try:
                logger.info("Installing npm packages...")
                result = subprocess.run(["npm", "install"], capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"npm install failed: {result.stderr}")
                
                logger.info("✅ Node.js dependencies installed successfully")
                
                # Count installed packages
                installed_packages = self._count_installed_npm_packages()
                
                self.installation_results.append(
                    InstallationResult(
                        component="Node.js Dependencies",
                        success=True,
                        message=f"Successfully installed {installed_packages} packages",
                        duration=time.time() - start_time,
                        details={"packages_count": installed_packages}
                    )
                )
                
                return True
                
            finally:
                os.chdir(original_dir)
            
        except Exception as e:
            logger.error(f"❌ Node.js dependency installation failed: {e}")
            
            self.installation_results.append(
                InstallationResult(
                    component="Node.js Dependencies",
                    success=False,
                    message=str(e),
                    duration=time.time() - start_time
                )
            )
            
            return False
    
    def _verify_installations(self) -> bool:
        """Verify critical installations"""
        logger.info("🔍 Verifying installations...")
        
        start_time = time.time()
        
        critical_python_packages = [
            "numpy", "pandas", "sklearn", "xgboost", "flask",
            "shap", "lime", "redis", "matplotlib", "plotly"
        ]
        
        verification_results = []
        
        for package in critical_python_packages:
            try:
                __import__(package)
                verification_results.append((package, True))
                logger.info(f"✅ {package}")
            except ImportError:
                verification_results.append((package, False))
                logger.warning(f"⚠️ {package} not importable")
        
        successful_imports = sum(1 for _, success in verification_results if success)
        total_packages = len(verification_results)
        
        success = successful_imports >= (total_packages * 0.8)  # 80% success rate
        
        self.installation_results.append(
            InstallationResult(
                component="Installation Verification",
                success=success,
                message=f"{successful_imports}/{total_packages} critical packages verified",
                duration=time.time() - start_time,
                details={
                    "verified_packages": [pkg for pkg, success in verification_results if success],
                    "failed_packages": [pkg for pkg, success in verification_results if not success]
                }
            )
        )
        
        return success
    
    def _count_installed_python_packages(self) -> int:
        """Count installed Python packages"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "list", "--format=json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return len(packages)
        except:
            pass
        return 0
    
    def _count_installed_npm_packages(self) -> int:
        """Count installed npm packages"""
        try:
            node_modules = self.frontend_dir / "node_modules"
            if node_modules.exists():
                return len([d for d in node_modules.iterdir() if d.is_dir() and not d.name.startswith('.')])
        except:
            pass
        return 0
    
    def _generate_installation_report(self):
        """Generate comprehensive installation report"""
        logger.info("\n" + "="*60)
        logger.info("📋 INSTALLATION REPORT")
        logger.info("="*60)
        
        total_time = sum(result.duration for result in self.installation_results)
        successful_components = sum(1 for result in self.installation_results if result.success)
        total_components = len(self.installation_results)
        
        logger.info(f"Overall Success Rate: {successful_components}/{total_components} components")
        logger.info(f"Total Installation Time: {total_time:.2f} seconds")
        logger.info("")
        
        for result in self.installation_results:
            status = "✅" if result.success else "❌"
            logger.info(f"{status} {result.component}")
            logger.info(f"   Message: {result.message}")
            logger.info(f"   Duration: {result.duration:.2f}s")
            
            if result.details:
                for key, value in result.details.items():
                    logger.info(f"   {key}: {value}")
            logger.info("")
        
        logger.info("="*60)

def main():
    """Main installation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install all dependencies for the Advanced Eco-Score Prediction System")
    parser.add_argument("--project-root", default=None, help="Project root directory")
    parser.add_argument("--python-only", action="store_true", help="Install only Python dependencies")
    parser.add_argument("--nodejs-only", action="store_true", help="Install only Node.js dependencies")
    
    args = parser.parse_args()
    
    # Create dependency manager
    dep_manager = DependencyManager(project_root=args.project_root)
    
    # Install dependencies based on arguments
    if args.python_only:
        success = dep_manager._install_python_dependencies()
    elif args.nodejs_only:
        success = dep_manager._install_nodejs_dependencies()
    else:
        success = dep_manager.install_all_dependencies()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()