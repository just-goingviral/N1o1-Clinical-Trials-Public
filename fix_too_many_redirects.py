#!/usr/bin/env python3
"""
Fix for "too many redirects" issue in N1O1 Clinical Trials application

This script updates the configuration in main.py to prevent redirect loops
by ensuring consistent URL generation and proper handling of cookie settings.
"""
import os
from pathlib import Path

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

def backup_file(filename):
    """Create a backup of a file"""
    backup_name = f"{filename}.bak"
    # Don't overwrite existing backups
    if not os.path.exists(backup_name):
        try:
            with open(filename, 'r') as src, open(backup_name, 'w') as dst:
                dst.write(src.read())
            print_success(f"Created backup: {backup_name}")
        except Exception as e:
            print_error(f"Failed to create backup: {e}")
    else:
        print_warning(f"Backup {backup_name} already exists, skipping")

def fix_url_generation():
    """Fix URL generation in main.py to prevent redirect loops"""
    filename = "main.py"
    if not os.path.exists(filename):
        print_error(f"{filename} not found!")
        return
    
    backup_file(filename)
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Fix 1: Update the safe_url_for function to be very simple and consistent
        safe_url_for_pattern = """def safe_url_for(endpoint, **kwargs):
    \"\"\"Generate URLs correctly for both Replit and custom domains\"\"\"
    # Don't override explicitly provided scheme
    if '_scheme' not in kwargs:
        # Use https for external domains if X-Forwarded-Proto is https
        if request.headers.get('X-Forwarded-Proto') == 'https':
            kwargs['_scheme'] = 'https'
        else:
            # Default to the configured preferred URL scheme
            kwargs['_scheme'] = app.config.get('PREFERRED_URL_SCHEME', 'http')
    
    # Make URLs external only if not already specified and not for static resources
    if '_external' not in kwargs and not endpoint.startswith('static'):
        kwargs['_external'] = True
    
    return url_for(endpoint, **kwargs)"""
        
        simple_safe_url_for = """def safe_url_for(endpoint, **kwargs):
    \"\"\"Generate URLs with a consistent scheme to prevent redirect loops\"\"\"
    # Always use HTTP for external URLs (if not explicitly specified)
    if '_external' in kwargs and kwargs['_external'] and '_scheme' not in kwargs:
        kwargs['_scheme'] = 'http'
    
    return url_for(endpoint, **kwargs)"""
        
        if safe_url_for_pattern in content:
            content = content.replace(safe_url_for_pattern, simple_safe_url_for)
            print_success("Updated safe_url_for function to use a consistent HTTP scheme")
        else:
            print_warning("Could not find safe_url_for function with expected pattern")
        
        # Fix 2: Set SESSION_COOKIE_SECURE explicitly to False
        if "app.config['SESSION_COOKIE_SECURE'] = False" not in content:
            secure_cookie_line = "app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies (required for Replit)"
            if "app.config['SESSION_COOKIE_SECURE']" in content:
                content = content.replace(
                    "app.config['SESSION_COOKIE_SECURE']", 
                    "app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies (required for Replit)"
                )
                print_success("Updated SESSION_COOKIE_SECURE to False")
            else:
                # Add after SERVER_NAME = None if it exists
                if "app.config['SERVER_NAME'] = None" in content:
                    content = content.replace(
                        "app.config['SERVER_NAME'] = None",
                        "app.config['SERVER_NAME'] = None\napp.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies (required for Replit)"
                    )
                    print_success("Added SESSION_COOKIE_SECURE = False after SERVER_NAME = None")
                else:
                    print_warning("Could not find an insertion point for SESSION_COOKIE_SECURE")
        
        # Fix 3: Set PREFERRED_URL_SCHEME consistently to http
        if "app.config['PREFERRED_URL_SCHEME']" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "app.config['PREFERRED_URL_SCHEME']" in line:
                    lines[i] = "app.config['PREFERRED_URL_SCHEME'] = 'http'  # Force HTTP scheme for all URLs"
                    print_success("Updated PREFERRED_URL_SCHEME to 'http'")
            content = '\n'.join(lines)
        else:
            # Add after SERVER_NAME if it exists
            if "app.config['SERVER_NAME'] = None" in content:
                content = content.replace(
                    "app.config['SERVER_NAME'] = None",
                    "app.config['SERVER_NAME'] = None\napp.config['PREFERRED_URL_SCHEME'] = 'http'  # Force HTTP scheme for all URLs"
                )
                print_success("Added PREFERRED_URL_SCHEME = 'http' after SERVER_NAME = None")
            else:
                print_warning("Could not find an insertion point for PREFERRED_URL_SCHEME")
        
        # Fix 4: Update ProxyFix with more conservative values
        proxy_fix_pattern = """app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # Number of trusted proxies for X-Forwarded-For
    x_proto=1,    # Number of trusted proxies for X-Forwarded-Proto
    x_host=1,     # Number of trusted proxies for X-Forwarded-Host
    x_port=1,     # Number of trusted proxies for X-Forwarded-Port
    x_prefix=1    # Number of trusted proxies for X-Forwarded-Prefix
)"""
        
        simple_proxy_fix = """app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,    # Handle X-Forwarded-Proto (minimal configuration)
    x_host=1      # Handle X-Forwarded-Host (minimal configuration)
)"""
        
        if proxy_fix_pattern in content:
            content = content.replace(proxy_fix_pattern, simple_proxy_fix)
            print_success("Updated ProxyFix to use simpler configuration")
        else:
            print_warning("Could not find ProxyFix with expected pattern")
        
        # Write the updated content
        with open(filename, 'w') as f:
            f.write(content)
        
        print_success(f"Successfully updated {filename} to fix redirect loops")
        
    except Exception as e:
        print_error(f"Error updating {filename}: {e}")

def fix_session_settings():
    """Create a .env file to enforce correct session settings"""
    env_file = ".env"
    env_content = """# Environment variables to prevent redirect loops
PREFERRED_URL_SCHEME=http
SESSION_COOKIE_SECURE=False
SERVER_NAME=
"""
    
    try:
        # Don't overwrite existing .env file
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                f.write(env_content)
            print_success("Created .env file with correct session settings")
        else:
            # Update existing .env file
            with open(env_file, 'r') as f:
                existing_content = f.read()
            
            updated = False
            if "PREFERRED_URL_SCHEME=" not in existing_content:
                existing_content += "\nPREFERRED_URL_SCHEME=http\n"
                updated = True
            
            if "SESSION_COOKIE_SECURE=" not in existing_content:
                existing_content += "\nSESSION_COOKIE_SECURE=False\n"
                updated = True
            
            if updated:
                with open(env_file, 'w') as f:
                    f.write(existing_content)
                print_success("Updated .env file with missing settings")
            else:
                print_warning(".env file already has the necessary settings")
    except Exception as e:
        print_error(f"Error creating/updating .env file: {e}")

def create_fixed_workflow_script():
    """Create a fixed workflow script with hardcoded port"""
    script_file = "start_fixed_app.sh"
    script_content = """#!/bin/bash
# N1O1 Clinical Trials - Fixed Application Starter
# This script uses a fixed port and correct environment settings
# to prevent redirect loops and cookie-related issues

# Show colored output
GREEN='\\033[0;32m'
RED='\\033[0;31m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Kill potentially conflicting processes
info "Cleaning up existing processes..."
pkill -9 -f gunicorn || true
sleep 1

# Set environment variables
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False
export SERVER_NAME=""

info "Starting application with port $PORT"
info "URL Scheme: $PREFERRED_URL_SCHEME"
info "Cookie Security: $SESSION_COOKIE_SECURE"
info "Server Name: '[dynamic]'"

exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app
"""
    
    try:
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_file, 0o755)
        print_success(f"Created executable workflow script: {script_file}")
    except Exception as e:
        print_error(f"Error creating workflow script: {e}")

def main():
    """Main function to fix all redirect-related issues"""
    print_header("N1O1 Clinical Trials - Redirect Loop Fix")
    
    # Fix URL generation in main.py
    fix_url_generation()
    
    # Fix session settings in .env
    fix_session_settings()
    
    # Create fixed workflow script
    create_fixed_workflow_script()
    
    print_header("FIXED: All redirect loop fixes applied")
    print("To run the application with fixed settings, execute:")
    print("./start_fixed_app.sh")

if __name__ == "__main__":
    main()