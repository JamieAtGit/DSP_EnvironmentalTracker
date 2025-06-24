#!/usr/bin/env python3
"""
🚀 One-Click Demo Launcher
=========================

Launches the complete eco-score prediction system demo including:
1. Backend Flask API
2. Frontend React application  
3. Advanced ML monitoring frameworks
4. Comprehensive analysis reports

Usage: python launch_demo.py
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path
import signal

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m' 
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.OKGREEN):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.ENDC}")

def print_header(text):
    """Print section header"""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f"🚀 {text}", Colors.HEADER)
    print_colored(f"{'='*60}", Colors.HEADER)

def check_dependencies():
    """Check if required dependencies are available"""
    print_header("Checking Dependencies")
    
    required_packages = [
        ('flask', 'Flask'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn'),
        ('xgboost', 'XGBoost')
    ]
    
    missing_packages = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print_colored(f"✅ {name} - Available", Colors.OKGREEN)
        except ImportError:
            print_colored(f"❌ {name} - Missing", Colors.FAIL)
            missing_packages.append(package)
    
    if missing_packages:
        print_colored(f"\n⚠️ Missing packages: {', '.join(missing_packages)}", Colors.WARNING)
        print_colored("Run: pip install flask pandas numpy scikit-learn xgboost matplotlib seaborn plotly", Colors.WARNING)
        return False
    
    print_colored("\n✅ All dependencies available!", Colors.OKGREEN)
    return True

def check_node_dependencies():
    """Check if Node.js and npm are available"""
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        print_colored("✅ Node.js and npm - Available", Colors.OKGREEN)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("❌ Node.js/npm not found", Colors.WARNING)
        print_colored("Frontend will be skipped - backend demo only", Colors.WARNING)
        return False

def run_backend():
    """Launch the Flask backend server"""
    print_header("Starting Backend Server")
    
    backend_dir = Path(__file__).parent / "backend" / "api"
    
    if not backend_dir.exists():
        print_colored(f"❌ Backend directory not found: {backend_dir}", Colors.FAIL)
        return None
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_APP'] = 'app.py'
    env['PYTHONPATH'] = str(Path(__file__).parent)
    
    try:
        # Start Flask server
        print_colored(f"📍 Starting Flask server in: {backend_dir}", Colors.OKBLUE)
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        
        if process.poll() is None:
            print_colored("✅ Backend server started successfully!", Colors.OKGREEN)
            print_colored("🌐 API available at: http://localhost:5000", Colors.OKCYAN)
            return process
        else:
            print_colored("❌ Backend server failed to start", Colors.FAIL)
            return None
            
    except Exception as e:
        print_colored(f"❌ Error starting backend: {e}", Colors.FAIL)
        return None

def run_frontend():
    """Launch the React frontend server"""
    print_header("Starting Frontend Server")
    
    frontend_dir = Path(__file__).parent / "frontend" / "website"
    
    if not frontend_dir.exists():
        print_colored(f"❌ Frontend directory not found: {frontend_dir}", Colors.FAIL)
        return None
    
    try:
        # Check if node_modules exists
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print_colored("📦 Installing frontend dependencies...", Colors.WARNING)
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        
        # Start development server
        print_colored(f"📍 Starting React server in: {frontend_dir}", Colors.OKBLUE)
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(5)
        
        if process.poll() is None:
            print_colored("✅ Frontend server started successfully!", Colors.OKGREEN)
            print_colored("🌐 Web app available at: http://localhost:5173", Colors.OKCYAN)
            return process
        else:
            print_colored("❌ Frontend server failed to start", Colors.FAIL)
            return None
            
    except Exception as e:
        print_colored(f"❌ Error starting frontend: {e}", Colors.FAIL)
        return None

def run_ml_frameworks():
    """Run the advanced ML frameworks for demonstration"""
    print_header("Running Advanced ML Frameworks")
    
    frameworks = [
        {
            'name': 'Enhanced Interpretability Framework',
            'path': 'backend/ml/evaluation/enhanced_interpretability_framework.py',
            'description': 'LIME explanations, decision boundaries, feature importance analysis'
        },
        {
            'name': 'Real-World Validation Study', 
            'path': 'backend/ml/evaluation/real_world_validation_study.py',
            'description': 'External validation, calibration analysis, domain adaptation'
        },
        {
            'name': 'Advanced Production Dashboard',
            'path': 'backend/ml/monitoring/advanced_production_dashboard.py', 
            'description': 'Real-time monitoring, adversarial detection, business metrics'
        }
    ]
    
    base_dir = Path(__file__).parent
    
    for framework in frameworks:
        framework_path = base_dir / framework['path']
        
        if framework_path.exists():
            print_colored(f"\n🔬 Running: {framework['name']}", Colors.OKBLUE)
            print_colored(f"📋 {framework['description']}", Colors.OKCYAN)
            
            try:
                # Set environment
                env = os.environ.copy()
                env['PYTHONPATH'] = str(base_dir)
                
                # Run framework in background
                process = subprocess.Popen(
                    [sys.executable, str(framework_path)],
                    cwd=base_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                
                # Let it run for a bit
                time.sleep(2)
                
                print_colored(f"✅ {framework['name']} started", Colors.OKGREEN)
                
            except Exception as e:
                print_colored(f"⚠️ Error running {framework['name']}: {e}", Colors.WARNING)
        else:
            print_colored(f"⚠️ Framework not found: {framework_path}", Colors.WARNING)

def open_browser():
    """Open web browser to demo URLs"""
    print_header("Opening Demo in Browser")
    
    urls = [
        "http://localhost:5173",  # Frontend
        "http://localhost:5000",  # Backend API
    ]
    
    time.sleep(3)  # Wait for servers to be ready
    
    for url in urls:
        try:
            print_colored(f"🌐 Opening: {url}", Colors.OKCYAN)
            webbrowser.open(url)
            time.sleep(1)
        except Exception as e:
            print_colored(f"⚠️ Could not open browser for {url}: {e}", Colors.WARNING)

def cleanup_processes(processes):
    """Clean up all running processes"""
    print_header("Shutting Down Demo")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                time.sleep(2)
                if process.poll() is None:
                    process.kill()
                print_colored("✅ Process terminated", Colors.OKGREEN)
            except Exception as e:
                print_colored(f"⚠️ Error terminating process: {e}", Colors.WARNING)

def main():
    """Main demo launcher function"""
    
    print_colored("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                🚀 Eco-Score ML System Demo                  ║
    ║                                                              ║
    ║  Complete production-ready system with advanced frameworks  ║
    ║  • Model Interpretability (LIME, SHAP, Decision Boundaries) ║
    ║  • Real-World Validation (External datasets, Calibration)   ║
    ║  • Production Monitoring (Real-time, Business Intelligence) ║
    ╚══════════════════════════════════════════════════════════════╝
    """, Colors.HEADER)
    
    processes = []
    
    try:
        # Check dependencies
        if not check_dependencies():
            print_colored("\n❌ Missing Python dependencies. Please install them first.", Colors.FAIL)
            return
        
        node_available = check_node_dependencies()
        
        # Start backend
        backend_process = run_backend()
        if backend_process:
            processes.append(backend_process)
        
        # Start frontend (if Node.js available)
        if node_available:
            frontend_process = run_frontend()
            if frontend_process:
                processes.append(frontend_process)
        
        # Run ML frameworks
        run_ml_frameworks()
        
        # Open browser
        if backend_process or (node_available and frontend_process):
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Keep demo running
        print_header("Demo Running Successfully!")
        print_colored("🎯 Available Services:", Colors.OKGREEN)
        if backend_process:
            print_colored("   • Backend API: http://localhost:5000", Colors.OKCYAN)
        if node_available and frontend_process:
            print_colored("   • Frontend App: http://localhost:5173", Colors.OKCYAN)
        
        print_colored("\n💡 Advanced Frameworks:", Colors.OKGREEN)
        print_colored("   • Check results directories for generated reports", Colors.OKCYAN)
        print_colored("   • Run individual frameworks manually for detailed analysis", Colors.OKCYAN)
        
        print_colored(f"\n🛑 Press Ctrl+C to stop the demo", Colors.WARNING)
        
        # Wait for interrupt
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print_colored("\n\n🛑 Demo interrupted by user", Colors.WARNING)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.FAIL)
    finally:
        cleanup_processes(processes)
        print_colored("\n✅ Demo shutdown complete!", Colors.OKGREEN)
        print_colored("Thank you for using the Eco-Score ML System Demo! 🚀", Colors.HEADER)

if __name__ == "__main__":
    main()