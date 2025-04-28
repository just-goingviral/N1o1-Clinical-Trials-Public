#!/usr/bin/env python3
"""
Update workflow launcher to fix the PORT issue for the N1O1 Clinical Trials application
"""
import os
import sys
import json
import subprocess
from datetime import datetime

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

def main():
    """Main function"""
    print_header("N1O1 Clinical Trials - Fixing Workflow Configuration")
    
    # Create a new workflow launcher script
    new_script = "workflow_launcher.sh"
    script_content = """#!/bin/bash
# N1O1 Clinical Trials - Fixed Workflow Launcher
# This script launches the application with a properly configured environment

# Make sure the port is correctly set
export PORT=5000

# Use our fixed application starter
./start_app_with_fixed_port.sh
"""
    
    try:
        with open(new_script, "w") as f:
            f.write(script_content)
        
        # Make it executable
        os.chmod(new_script, 0o755)
        print_success(f"Created {new_script} with fixed port configuration")
        
        # Create a symbolic link for the workflow
        workflow_link = "start_application.sh"
        if os.path.exists(workflow_link):
            os.remove(workflow_link)
        
        os.symlink(new_script, workflow_link)
        print_success(f"Created symbolic link {workflow_link} -> {new_script}")
        
        # Print usage instructions
        print("\nTo start the application with fixed PORT configuration:")
        print(f"  1. ./workflow_launcher.sh")
        print(f"  2. ./start_app_with_fixed_port.sh")
        
        return 0
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())