#!/usr/bin/env python3
"""
Fix deployment issues with the N1O1 Clinical Trials application.

This script makes the application work correctly both on Replit's internal domain
and on custom domains by applying proper URL generation and proxy handling.
"""
import os
import sys
import re
import shutil
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

def backup_file(filename):
    """Create a backup of a file"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"{filename}.bak_{timestamp}"
    try:
        shutil.copy2(filename, backup_filename)
        print_success(f"Created backup: {backup_filename}")
        return True
    except Exception as e:
        print_error(f"Failed to create backup of {filename}: {e}")
        return False

def fix_main_py():
    """Fix issues in main.py"""
    filename = "main.py"
    if not os.path.exists(filename):
        print_error(f"{filename} not found")
        return False
    
    # Create backup
    if not backup_file(filename):
        return False
    
    print_header("Fixing main.py for deployment compatibility")
    
    with open(filename, "r") as f:
        content = f.read()
    
    # Fix 1: Remove duplicate configuration blocks
    # Find the first CRITICAL REDIRECT FIX block and remove duplicates
    first_block_pattern = r"# === CRITICAL REDIRECT FIX ===.*?app\.config\['REMEMBER_COOKIE_SECURE'\] = False.*?\n\n"
    blocks = re.findall(first_block_pattern, content, re.DOTALL)
    if len(blocks) > 1:
        print_warning(f"Found {len(blocks)} duplicate configuration blocks, keeping only the first one")
        # Keep only the first block
        for block in blocks[1:]:
            content = content.replace(block, "")
    
    # Fix 2: Remove hardcoded PREFERRED_URL_SCHEME and use dynamic determination
    content = content.replace(
        "app.config['PREFERRED_URL_SCHEME'] = 'http'",
        "app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME', 'http')"
    )
    
    # Fix 3: Improve the safe_url_for function to be more intelligent
    safe_url_for_pattern = r"def safe_url_for\(endpoint, \*\*kwargs\):.*?return url_for\(endpoint, \*\*kwargs\)"
    safe_url_for_replacement = """def safe_url_for(endpoint, **kwargs):
    """Generate URLs correctly for both internal and external domains"""
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
    
    content = re.sub(safe_url_for_pattern, safe_url_for_replacement, content, flags=re.DOTALL)
    
    # Fix 4: Improve the safe_redirect function to work with dynamic protocol
    safe_redirect_pattern = r"def safe_redirect\(endpoint, \*\*kwargs\):.*?return redirect\(url_for\(endpoint, \*\*kwargs\)\)"
    safe_redirect_replacement = """def safe_redirect(endpoint, **kwargs):
    '''Generate a redirect that works with both http and https'''
    # Use safe_url_for to generate the URL with the correct scheme
    target = safe_url_for(endpoint, **kwargs)
    return redirect(target)"""
    
    content = re.sub(safe_redirect_pattern, safe_redirect_replacement, content, flags=re.DOTALL)
    
    # Fix 5: Update ProxyFix to be more robust
    proxy_fix_pattern = r"app.wsgi_app = ProxyFix\(.*?\)"
    proxy_fix_replacement = """app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # Number of trusted proxies for X-Forwarded-For
    x_proto=1,    # Number of trusted proxies for X-Forwarded-Proto
    x_host=1,     # Number of trusted proxies for X-Forwarded-Host
    x_port=1,     # Number of trusted proxies for X-Forwarded-Port
    x_prefix=1    # Number of trusted proxies for X-Forwarded-Prefix
)"""
    
    content = re.sub(proxy_fix_pattern, proxy_fix_replacement, content, flags=re.DOTALL)
    
    # Fix 6: Fix hardcoded HTTP in redirects
    content = content.replace(
        "return redirect(url_for('patients.list_patients', _scheme='http', _external=True))",
        "return safe_redirect('patients.list_patients')"
    )
    
    # Fix 7: Ensure SERVER_NAME is None to let the request determine server name
    if "app.config['SERVER_NAME'] = None" not in content:
        # Insert after app creation
        app_creation = "app = Flask(__name__)"
        server_name_config = app_creation + "\n\n# Let request determine server name\napp.config['SERVER_NAME'] = None"
        content = content.replace(app_creation, server_name_config)
    
    # Write the updated content
    with open(filename, "w") as f:
        f.write(content)
    
    print_success(f"Updated {filename} with deployment fixes")
    return True

def fix_redirect_calls_in_all_routes():
    """Fix hardcoded redirect and url_for calls in route files"""
    routes_dir = "routes"
    if not os.path.exists(routes_dir):
        print_error(f"{routes_dir} directory not found")
        return False
    
    print_header(f"Fixing redirect and url_for calls in {routes_dir}")
    
    # Pattern to find hardcoded HTTP schemes in redirect and url_for calls
    redirect_pattern = r"redirect\(url_for\([^,]+, _scheme=['\"]http['\"]"
    url_for_pattern = r"url_for\([^,]+, _scheme=['\"]http['\"]"
    
    file_count = 0
    fixed_count = 0
    
    for root, _, files in os.walk(routes_dir):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            
            filepath = os.path.join(root, filename)
            file_count += 1
            
            # Read file content
            with open(filepath, "r") as f:
                content = f.read()
            
            # Check if fixes are needed
            if re.search(redirect_pattern, content) or re.search(url_for_pattern, content):
                # Create backup
                if not backup_file(filepath):
                    continue
                
                # Replace hardcoded redirects
                original_content = content
                
                # Fix redirect calls to use safe_redirect
                content = re.sub(
                    r"redirect\(url_for\(([^,]+), _scheme=['\"]http['\"], _external=True[^\)]*\)\)",
                    r"safe_redirect(\1)",
                    content
                )
                
                # Fix url_for calls to use safe_url_for
                content = re.sub(
                    r"url_for\(([^,]+), _scheme=['\"]http['\"], _external=True[^\)]*\)",
                    r"safe_url_for(\1)",
                    content
                )
                
                # Add imports if needed
                if content != original_content:
                    if "from main import safe_redirect, safe_url_for" not in content:
                        # Add import
                        if "from main import" in content:
                            # Extend existing import
                            content = re.sub(
                                r"from main import ([^\n]+)",
                                r"from main import \1, safe_redirect, safe_url_for",
                                content
                            )
                        else:
                            # Add new import after existing imports
                            import_pattern = r"(import [^\n]+\n)"
                            last_import = re.findall(import_pattern, content)
                            if last_import:
                                last_import = last_import[-1]
                                content = content.replace(
                                    last_import,
                                    last_import + "\nfrom main import safe_redirect, safe_url_for\n"
                                )
                            else:
                                # Add at the top
                                content = "from main import safe_redirect, safe_url_for\n\n" + content
                    
                    # Write updated content
                    with open(filepath, "w") as f:
                        f.write(content)
                    
                    fixed_count += 1
                    print_success(f"Fixed {filepath}")
    
    print_success(f"Examined {file_count} route files, fixed {fixed_count} files")
    return True

def create_env_file():
    """Create a .env file with deployment configuration"""
    env_file = ".env"
    if os.path.exists(env_file):
        print_warning(f"{env_file} already exists, making backup")
        backup_file(env_file)
    
    print_header("Creating deployment configuration in .env")
    
    # Create the .env file with deployment-friendly settings
    env_content = """# N1O1 Clinical Trials Deployment Configuration
# Generated by fix_deployment.py

# === URL Generation Settings ===
PREFERRED_URL_SCHEME=http
SERVER_NAME=
FLASK_ENV=production

# === Session Security Settings ===
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# === Application Settings ===
PORT=5000
FLASK_DEBUG=0
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print_success(f"Created {env_file} with deployment configuration")
    return True

def create_load_env_script():
    """Create a script to load environment variables"""
    script_file = "load_env.sh"
    if os.path.exists(script_file):
        print_warning(f"{script_file} already exists, making backup")
        backup_file(script_file)
    
    print_header(f"Creating {script_file} to load environment variables")
    
    script_content = """#!/bin/bash
# Load environment variables for N1O1 Clinical Trials
# Generated by fix_deployment.py

# Source the .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  set -a
  source .env
  set +a
else
  echo "No .env file found"
fi

# Apply deployment-friendly settings
export PREFERRED_URL_SCHEME=${PREFERRED_URL_SCHEME:-http}
export SESSION_COOKIE_SECURE=${SESSION_COOKIE_SECURE:-False}
export SERVER_NAME=${SERVER_NAME:-""}
export PORT=${PORT:-5000}
export FLASK_DEBUG=${FLASK_DEBUG:-0}
export FLASK_ENV=${FLASK_ENV:-production}

echo "Deployment settings loaded:"
echo "- PREFERRED_URL_SCHEME: $PREFERRED_URL_SCHEME"
echo "- SESSION_COOKIE_SECURE: $SESSION_COOKIE_SECURE"
echo "- SERVER_NAME: $SERVER_NAME"
echo "- PORT: $PORT"
echo "- FLASK_DEBUG: $FLASK_DEBUG"
echo "- FLASK_ENV: $FLASK_ENV"
"""
    
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    
    print_success(f"Created executable {script_file}")
    return True

def create_start_script():
    """Create an improved startup script"""
    script_file = "start_deployment.sh"
    if os.path.exists(script_file):
        print_warning(f"{script_file} already exists, making backup")
        backup_file(script_file)
    
    print_header(f"Creating {script_file} for consistent deployments")
    
    script_content = """#!/bin/bash
# Deployment-friendly startup script for N1O1 Clinical Trials
# Generated by fix_deployment.py

# Load environment variables
source ./load_env.sh

# Clean up any existing processes
if [ -z "$PORT" ]; then
  PORT=5000
fi
echo "Cleaning up processes on port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || echo "No processes to clean up"
sleep 1

# Verify the app is runnable
echo "Verifying application..."
if [ ! -f "main.py" ]; then
  echo "Error: main.py not found"
  exit 1
fi

# Start the app with gunicorn
echo "Starting N1O1 Clinical Trials on port $PORT..."
exec gunicorn \\
  --bind 0.0.0.0:$PORT \\
  --workers 1 \\
  --timeout 300 \\
  --keep-alive 120 \\
  --log-level info \\
  --reload \\
  main:app
"""
    
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    
    print_success(f"Created executable {script_file}")
    return True

def update_procfile():
    """Update Procfile for web deployment"""
    procfile = "Procfile"
    
    print_header(f"Updating {procfile} for deployments")
    
    # Create or update Procfile
    procfile_content = "web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --keep-alive 120 main:app\n"
    
    with open(procfile, "w") as f:
        f.write(procfile_content)
    
    print_success(f"Updated {procfile} for web deployments")
    return True

def main():
    """Main function to run all fixes"""
    print_header("N1O1 Clinical Trials Deployment Fix")
    print("This script will fix deployment issues to make the application work")
    print("correctly on both Replit and custom domains.")
    print("")
    
    success = True
    
    # Fix main.py
    if not fix_main_py():
        success = False
    
    # Fix route files
    if not fix_redirect_calls_in_all_routes():
        success = False
    
    # Create deployment configuration
    if not create_env_file():
        success = False
    
    # Create environment loader script
    if not create_load_env_script():
        success = False
    
    # Create improved startup script
    if not create_start_script():
        success = False
    
    # Update Procfile
    if not update_procfile():
        success = False
    
    # Print final status
    if success:
        print_header("Deployment fixes completed successfully!")
        print("Your application is now deployment-ready. To start it:")
        print("1. Run: ./start_deployment.sh")
        print("2. For custom domains, no additional configuration is needed")
        print("3. For Replit deployments, the configuration is already optimized")
    else:
        print_header("Some fixes failed, please check the errors above")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())