
import sys
import os
import subprocess
import time
import requests

def test_deployment_configuration():
    """Test the deployment configuration to ensure it works properly"""
    print("=== Testing Deployment Configuration ===")
    
    # Check current directory and files
    print(f"Working directory: {os.getcwd()}")
    
    # Validate Procfile
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            procfile_content = f.read().strip()
            print(f"Procfile content: {procfile_content}")
    else:
        print("WARNING: Procfile not found")
    
    # Validate run.sh
    if os.path.exists('run.sh'):
        with open('run.sh', 'r') as f:
            run_sh_content = f.read()
            print(f"run.sh exists and contains {len(run_sh_content)} characters")
        # Check if run.sh is executable
        is_executable = os.access('run.sh', os.X_OK)
        print(f"run.sh is executable: {is_executable}")
        if not is_executable:
            print("Making run.sh executable...")
            os.chmod('run.sh', 0o755)
    else:
        print("WARNING: run.sh not found")
    
    # Check if we can import the main app
    try:
        from main import app
        print("Successfully imported main Flask app")
    except Exception as e:
        print(f"ERROR: Failed to import main Flask app: {str(e)}")
    
    # Try starting the server
    print("\nAttempting to start the server for 5 seconds...")
    try:
        process = subprocess.Popen(
            ["gunicorn", "--bind", "0.0.0.0:5001", "--timeout", "30", "main:app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Try connecting to the server
        try:
            response = requests.get("http://localhost:5001/system/health", timeout=3)
            print(f"Server response: {response.status_code}")
            print(f"Response content: {response.text[:100]}...")
        except requests.RequestException as e:
            print(f"Could not connect to server: {str(e)}")
        
        # Terminate the server after test
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        print(f"Server output: {stdout[:200]}...")
        if stderr:
            print(f"Server errors: {stderr[:200]}...")
    except Exception as e:
        print(f"Error testing server: {str(e)}")
    
    print("\n=== Deployment Test Complete ===")

if __name__ == "__main__":
    test_deployment_configuration()
