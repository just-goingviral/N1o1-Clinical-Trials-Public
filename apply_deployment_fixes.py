#!/usr/bin/env python3
"""
Apply deployment fixes to make the application work correctly on all domains

This script:
1. Updates all route files to use safe_redirect and safe_url_for
2. Ensures consistency in URL generation throughout the application
3. Makes the application work in both Replit internal and custom domains
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

def update_imports_in_file(filepath, modified_content):
    """Update imports in a file to include safe_redirect and safe_url_for"""
    # Add import for safe functions if needed
    if "from main import safe_redirect, safe_url_for" not in modified_content:
        # Find import section and add our import
        if "from main import" in modified_content:
            # Add to existing main import
            modified_content = re.sub(
                r"from main import ([^\n]+)",
                r"from main import \1, safe_redirect, safe_url_for",
                modified_content
            )
        else:
            # Add new import at the top of imports
            import_match = re.search(r"(from [^\n]+\n)", modified_content)
            if import_match:
                last_import = import_match.group(1)
                index = modified_content.rindex(last_import) + len(last_import)
                modified_content = (
                    modified_content[:index] + 
                    "from main import safe_redirect, safe_url_for\n" + 
                    modified_content[index:]
                )
            else:
                # Add at the top of the file
                modified_content = "from main import safe_redirect, safe_url_for\n" + modified_content
        
        print_success(f"Added imports for safe_redirect and safe_url_for to {os.path.basename(filepath)}")
    
    return modified_content

def fix_url_for_in_file(filepath):
    """Fix url_for calls in a file to use safe_url_for"""
    try:
        # Read the file
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # First make a backup
        backup_file(filepath)
        
        # Replace redirect with url_for to use safe_redirect with correct URL generation
        modified_content = re.sub(
            r"redirect\(url_for\(([^,\)]+)(.*?)\)\)",
            r"safe_redirect(\1\2)",
            content
        )
        
        # Replace url_for with safe_url_for for consistent URL generation
        modified_content = re.sub(
            r"(?<!\w)url_for\(([^,\)]+)(.*?)\)",
            r"safe_url_for(\1\2)",
            modified_content
        )
        
        # Add imports if needed
        if modified_content != original_content:
            modified_content = update_imports_in_file(filepath, modified_content)
            
            # Write changes
            with open(filepath, 'w') as f:
                f.write(modified_content)
            
            print_success(f"Updated URL generation in {os.path.basename(filepath)}")
            return True
        else:
            print_warning(f"No changes needed in {os.path.basename(filepath)}")
            return False
    except Exception as e:
        print_error(f"Error updating {filepath}: {str(e)}")
        return False

def scan_routes_directory():
    """Scan routes directory for Python files and fix them"""
    print_header("Updating route files for deployment-agnostic URL generation")
    
    routes_dir = "routes"
    if not os.path.exists(routes_dir):
        print_error(f"Routes directory '{routes_dir}' not found")
        return False
    
    file_count = 0
    updated_count = 0
    
    for root, _, files in os.walk(routes_dir):
        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                file_count += 1
                
                if fix_url_for_in_file(filepath):
                    updated_count += 1
    
    print_success(f"Processed {file_count} route files, updated {updated_count} files")
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
# Generated by apply_deployment_fixes.py

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

def main():
    """Main function"""
    print_header("N1O1 Clinical Trials - Deployment Fixes")
    print("This script updates the application to handle URLs correctly on all deployment platforms")
    
    # Update route files to use safe_url_for and safe_redirect
    if not scan_routes_directory():
        print_error("Failed to update route files")
        return 1
    
    # Create environment configuration
    if not create_env_file():
        print_error("Failed to create environment configuration")
        return 1
    
    print_header("Deployment fixes completed successfully!")
    print("Your application should now work correctly on both Replit and custom domains.")
    print("To verify the deployment:")
    print("1. Use: python verify_deployment.py")
    print("2. Start the application with: ./workflow_fixed.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())