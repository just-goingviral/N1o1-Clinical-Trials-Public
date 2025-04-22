
import os
import sys
import subprocess

def check_environment():
    """Check the deployment environment"""
    print("=== Environment Checks ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Check if main database file exists
    db_path = 'no_dynamics.db'
    print(f"Database exists: {os.path.exists(db_path)}")
    
    # Check Flask and other critical dependencies
    try:
        import flask
        print(f"Flask version: {flask.__version__}")
        
        import numpy
        print(f"NumPy version: {numpy.__version__}")
        
        import matplotlib
        print(f"Matplotlib version: {matplotlib.__version__}")
        
        import pandas
        print(f"Pandas version: {pandas.__version__}")
        
        print("All critical dependencies loaded successfully!")
    except ImportError as e:
        print(f"Dependency error: {e}")
    
    # Check if gunicorn is available
    try:
        result = subprocess.run(['which', 'gunicorn'], 
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"Gunicorn found at: {result.stdout.strip()}")
        else:
            print("Gunicorn not found in PATH")
    except Exception as e:
        print(f"Error checking for gunicorn: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    check_environment()
    print("\nRun this command to test the Flask app directly:")
    print("python -c 'from main import app; app.run(host=\"0.0.0.0\", port=5000, debug=True)'")
