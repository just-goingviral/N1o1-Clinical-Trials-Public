#!/usr/bin/env python3
"""
Simple redirect loop fix for N1O1 Clinical Trials application

This script directly fixes main.py to address redirect issues and cookie problems.
"""
import os
import re

def main():
    """Apply fixes to prevent redirect loops"""
    # Check if we have a backup file, otherwise use the current main.py
    if os.path.exists('main.py.bak'):
        print("Restoring from backup file...")
        with open('main.py.bak', 'r') as f:
            content = f.read()
    else:
        print("No backup found, reading current main.py...")
        with open('main.py', 'r') as f:
            content = f.read()
        # Create a backup
        with open('main.py.bak', 'w') as f:
            f.write(content)
        print("Backup created as main.py.bak")
    
    print("Applying redirect loop fixes...")
    
    # Use a safer approach with string replacement for key lines
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Fix SESSION_COOKIE_SECURE
        if "app.config['SESSION_COOKIE_SECURE']" in line and "= True" in line:
            new_lines.append("app.config['SESSION_COOKIE_SECURE'] = False  # Force HTTP cookies to prevent redirect issues")
        # Fix PREFERRED_URL_SCHEME 
        elif "app.config['PREFERRED_URL_SCHEME']" in line:
            new_lines.append("app.config['PREFERRED_URL_SCHEME'] = 'http'  # Force HTTP scheme for URL generation")
        # Fix SERVER_NAME
        elif "app.config['SERVER_NAME']" in line:
            new_lines.append("app.config['SERVER_NAME'] = None  # Let request determine server name")
        else:
            new_lines.append(line)
    
    # Add critical cookie settings after app creation
    app_index = -1
    for i, line in enumerate(new_lines):
        if "app = Flask(__name__)" in line:
            app_index = i
            break
    
    if app_index >= 0:
        cookie_config = [
            "",
            "# === CRITICAL REDIRECT FIX ===",
            "# These settings are essential to prevent custom domain redirect loops",
            "app.config['PREFERRED_URL_SCHEME'] = 'http'  # Force URL generation to use HTTP scheme",
            "os.environ['WERKZEUG_RUN_MAIN'] = 'true'     # Prevent reloader from creating redirect loops",
            "app.config['SERVER_NAME'] = None             # Let the request determine server name",
            "# Fixed cookie and session settings to prevent redirect loops",
            "app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies",
            "app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies",
            "app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same site",
            "app.config['SESSION_COOKIE_PATH'] = '/'  # Set cookie path to root", 
            "app.config['SESSION_COOKIE_DOMAIN'] = None  # Will match the domain that made the request",
            "app.config['SESSION_REFRESH_EACH_REQUEST'] = False  # Don't refresh cookies on each request",
            "app.config['PREFERRED_URL_SCHEME'] = 'http'  # Force HTTP scheme for URL generation",
            "app.config['REMEMBER_COOKIE_SECURE'] = False  # Allow HTTP cookies for remember me",
            ""
        ]
        new_lines[app_index+1:app_index+1] = cookie_config
    
    # Write back the modified content
    with open('main.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("Redirect loop fixes applied successfully!")
    print("Please restart the application with: ./start_clean.sh")

if __name__ == "__main__":
    main()