#!/usr/bin/env python3
"""
Fix workflow issue with N1O1 Clinical Trials application

This script updates the workflow command to use a fixed port number
and proper environment settings to prevent redirect loops.
"""
import os
import subprocess
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_success(text):
    """Print a success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print an error message"""
    print(f"✗ {text}")

def update_workflow_command():
    """Update the workflow command file"""
    workflow_file = ".replit"
    new_command = "bash workflow_fixed.sh"
    
    print_header("Creating fixed workflow script")
    
    # Create the workflow script
    script_content = """#!/bin/bash
# Fixed workflow script for N1O1 Clinical Trials application
# This script uses a hardcoded port to prevent empty PORT variable issues

# Set a fixed port
export PORT=5000

# Set environment variables for URL handling
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False
export SERVER_NAME=""

# Start the application with the fixed port
exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app
"""
    
    try:
        with open("workflow_fixed.sh", "w") as f:
            f.write(script_content)
        
        # Make the script executable
        os.chmod("workflow_fixed.sh", 0o755)
        print_success("Created workflow_fixed.sh script with fixed port")
    except Exception as e:
        print_error(f"Failed to create workflow script: {e}")
        return False
    
    # Tell the user to update the workflow manually
    print_header("How to Fix the Workflow")
    print("1. In the Replit UI, click on 'Tools' > 'Secrets'")
    print("2. Add a new secret with key 'PORT' and value '5000'")
    print("3. Click 'Save'")
    print("4. Run the fixed workflow script manually:")
    print("   ./workflow_fixed.sh")
    print("\nThis will start the application with the correct port and environment settings.")
    
    return True

def main():
    """Main function"""
    print_header("N1O1 Clinical Trials - Workflow Fix")
    update_workflow_command()
    print_header("Fix Complete")
    print("To run the application with fixed settings:")
    print("  ./workflow_fixed.sh")

if __name__ == "__main__":
    main()