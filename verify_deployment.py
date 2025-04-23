
#!/usr/bin/env python
"""
Verify deployment readiness for N1O1 Clinical Trials
"""
import os
import sys
import requests
import subprocess
from datetime import datetime

def print_header(message):
    print(f"\n{'=' * 50}")
    print(f" {message}")
    print(f"{'=' * 50}")

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def print_error(message):
    print(f"❌ {message}")

def check_files():
    """Check for critical files"""
    print_header("Checking Critical Files")
    
    critical_files = [
        "main.py", 
        "models.py",
        "Procfile",
        "run_with_port.sh",
        "requirements.txt",
        ".replit"
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            print_success(f"Found {file}")
        else:
            print_error(f"Missing {file}")
            
    # Check recent module additions
    module_files = [
        "eligibility.py",
        "patient_education.py",
        "routes/chat_routes.py",
        "routes/consent_routes.py",
        "templates/consent_form.html"
    ]
    
    print("\nChecking new module files:")
    for file in module_files:
        if os.path.exists(file):
            print_success(f"Found {file}")
        else:
            print_error(f"Missing {file}")

def check_database():
    """Check database file"""
    print_header("Checking Database")
    
    db_file = "no_dynamics.db"
    if os.path.exists(db_file):
        size_mb = os.path.getsize(db_file) / (1024 * 1024)
        print_success(f"Database file exists: {db_file} ({size_mb:.2f} MB)")
    else:
        print_warning("Database file not found. Will be created on first run.")

def check_deployment_config():
    """Check deployment configuration"""
    print_header("Checking Deployment Configuration")
    
    # Check Procfile
    try:
        with open('Procfile', 'r') as f:
            procfile_content = f.read()
            if '$PORT' in procfile_content:
                print_success("Procfile correctly uses $PORT environment variable")
            else:
                print_warning("Procfile may not be using $PORT environment variable")
    except FileNotFoundError:
        print_error("Procfile not found")
        
    # Check .replit file for deployment settings
    try:
        with open('.replit', 'r') as f:
            replit_content = f.read()
            if 'deploymentTarget' in replit_content:
                print_success("Deployment target configured in .replit")
            else:
                print_warning("Deployment target may not be configured in .replit")
    except FileNotFoundError:
        print_error(".replit file not found")
    
    # Check run_with_port.sh
    if os.path.exists('run_with_port.sh'):
        if not os.access('run_with_port.sh', os.X_OK):
            print_warning("run_with_port.sh is not executable. Making it executable...")
            os.chmod('run_with_port.sh', 0o755)
            print_success("Made run_with_port.sh executable")
        else:
            print_success("run_with_port.sh is executable")
    else:
        print_error("run_with_port.sh not found")

def check_dependencies():
    """Check dependencies"""
    print_header("Checking Dependencies")
    
    required_packages = [
        "flask", "gunicorn", "openai", "sqlalchemy", 
        "flask_sqlalchemy", "matplotlib", "numpy"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is not installed")

def check_port():
    """Check if port is in use"""
    print_header("Checking Port Availability")
    
    port = os.environ.get('PORT', '5000')
    print_info(f"Checking port {port}")
    
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('localhost', int(port)))
        if result == 0:
            print_warning(f"Port {port} is in use. This may cause deployment issues.")
        else:
            print_success(f"Port {port} is available")
        s.close()
    except Exception as e:
        print_error(f"Error checking port: {str(e)}")

def print_info(message):
    print(f"ℹ️ {message}")

def main():
    """Main function"""
    print_header("N1O1 CLINICAL TRIALS DEPLOYMENT AUDIT")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_files()
    check_database()
    check_dependencies()
    check_deployment_config()
    check_port()
    
    print_header("AUDIT COMPLETE")
    print("To deploy your application:")
    print("1. Make sure the 'Run Flask App (Forced)' workflow works")
    print("2. Go to the Deployments tab")
    print("3. Click 'Deploy' to publish your application")

if __name__ == "__main__":
    main()
