#!/usr/bin/env python3
"""
Update workflow configuration for N1O1 Clinical Trials application
This script updates the workflow configuration to use fixed port and environment settings
"""
import json
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

def print_warning(text):
    """Print a warning message"""
    print(f"⚠ {text}")

def print_error(text):
    """Print an error message"""
    print(f"✗ {text}")

def create_workflow_config():
    """Create workflow configuration file"""
    config_path = "workflow_config.txt"
    config_content = """# Workflow configuration for N1O1 Clinical Trials application
# This file is used by update_workflow.py to configure the workflow

[workflow]
name = Start application
command = PORT=5000 PREFERRED_URL_SCHEME=http SESSION_COOKIE_SECURE=False SERVER_NAME= gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        print_success(f"Created workflow configuration at {config_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create workflow configuration: {e}")
        return False

def main():
    """Main function"""
    print_header("Updating Workflow Configuration")
    
    if create_workflow_config():
        print_success("Workflow configuration created successfully")
        print("\nTo use this configuration, please run:")
        print("./start_fixed_app.sh")
        
        # Create a message for the user
        message = """
IMPORTANT: To fix the "too many redirects" issue:

1. Manually restart the workflow from the Replit UI
2. Or run the fixed startup script:
   ./start_fixed_app.sh
   
This script provides the correct environment variables and fixed port
configuration to prevent redirect loops.
"""
        print(message)
    else:
        print_error("Failed to update workflow configuration")

if __name__ == "__main__":
    main()