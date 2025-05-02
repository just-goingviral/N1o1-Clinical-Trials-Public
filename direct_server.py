#!/usr/bin/env python3
"""
Direct server starter for N1O1 Clinical Trials
This version avoids any external dependencies or environment variables
"""
import subprocess
import sys

def main():
    """
    Start the server directly without environment variables
    """
    # Use fixed port without referencing environment variables
    port = "5000"
    
    print(f"Starting N1O1 Clinical Trials on port {port}...")
    
    # Use direct subprocess call to avoid shell interpretation
    try:
        # Call gunicorn directly
        subprocess.run([
            "gunicorn",
            "--bind", f"0.0.0.0:{port}",
            "--reuse-port",
            "--reload",
            "main:app"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
