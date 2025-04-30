#!/usr/bin/env python3
"""
Direct starter for the N1O1 Clinical Trials application
This bypasses workflow and runs Flask directly
"""
import os
import sys
import subprocess
import time
import signal
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Kill any existing processes on port 5000
def kill_port_process(port=5000):
    try:
        # Check if port is already in use
        result = subprocess.run(
            ["lsof", "-i", f":{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if "LISTEN" in result.stdout:
            logger.info(f"Found process using port {port}, attempting to kill...")
            
            # Extract PID(s)
            for line in result.stdout.splitlines()[1:]:  # Skip header
                if "LISTEN" in line:
                    pid = line.split()[1]
                    logger.info(f"Killing process {pid}")
                    os.kill(int(pid), signal.SIGTERM)
            
            # Give processes time to terminate
            time.sleep(1)
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error killing port process: {e}")
        return False

# Main function to start the Flask application
def start_flask_app():
    try:
        # Set required environment variables
        os.environ["PORT"] = "5000"
        os.environ["FLASK_APP"] = "main.py"
        os.environ["FLASK_ENV"] = "development"
        os.environ["PREFERRED_URL_SCHEME"] = "http"
        os.environ["SESSION_COOKIE_SECURE"] = "False"
        
        # Kill any existing processes on port 5000
        kill_port_process(5000)
        
        logger.info("Starting N1O1 Clinical Trials application on port 5000...")
        
        # Start Flask using its built-in server (more reliable for testing)
        flask_cmd = ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
        
        # Alternative: use gunicorn if flask server fails
        gunicorn_cmd = [
            "gunicorn", 
            "--bind", "0.0.0.0:5000", 
            "--workers", "1", 
            "--timeout", "120", 
            "--reload", 
            "main:app"
        ]
        
        try:
            # Try Flask first
            logger.info(f"Running command: {' '.join(flask_cmd)}")
            flask_process = subprocess.Popen(
                flask_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait briefly to see if it starts
            time.sleep(3)
            
            if flask_process.poll() is not None:
                logger.warning("Flask server failed to start. Trying gunicorn...")
                # Flask failed, try gunicorn
                logger.info(f"Running command: {' '.join(gunicorn_cmd)}")
                gunicorn_process = subprocess.Popen(
                    gunicorn_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait briefly to see if it starts
                time.sleep(3)
                
                if gunicorn_process.poll() is not None:
                    logger.error("Failed to start server with both Flask and gunicorn.")
                    stderr = gunicorn_process.stderr.read()
                    logger.error(f"Gunicorn error: {stderr}")
                    return False
                else:
                    logger.info("Server started with gunicorn successfully!")
                    return True
            else:
                logger.info("Server started with Flask successfully!")
                return True
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in start_flask_app: {e}")
        return False

if __name__ == "__main__":
    success = start_flask_app()
    
    if success:
        logger.info("N1O1 Clinical Trials application is running successfully on port 5000")
        
        # Keep script running
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Server stopping due to keyboard interrupt...")
    else:
        logger.error("Failed to start N1O1 Clinical Trials application")
        sys.exit(1)