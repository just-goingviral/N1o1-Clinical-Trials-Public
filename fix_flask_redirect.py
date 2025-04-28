#!/usr/bin/env python3
"""
Fix Flask redirect loops with custom domains
This script updates Flask application code to prevent redirect loops
when using custom domains, especially with Netlify or similar hosts.
"""
import os
import re
import sys
from pathlib import Path

def find_flask_app_files():
    """Find potential Flask app files"""
    app_files = []
    for file in ["app.py", "main.py", "application.py", "server.py"]:
        if os.path.exists(file):
            app_files.append(file)
    
    return app_files

def fix_flask_app(file_path):
    """Fix Flask app configuration to prevent redirect loops"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    changes_made = False
    
    # Add or update PREFERRED_URL_SCHEME
    if "app.config['PREFERRED_URL_SCHEME']" not in content:
        preferred_scheme = "app.config['PREFERRED_URL_SCHEME'] = 'http'  # Prevent redirect loops with custom domains"
        
        # Find where other app.config items are set
        config_match = re.search(r"app\.config\[.+\].+\n", content)
        if config_match:
            # Insert after the last app.config line
            last_config_pos = content.rindex("app.config")
            end_of_line = content.find("\n", last_config_pos) + 1
            content = content[:end_of_line] + preferred_scheme + "\n" + content[end_of_line:]
        else:
            # Add after app initialization
            app_init_match = re.search(r"app\s*=\s*Flask\(.+\)", content)
            if app_init_match:
                end_pos = content.find("\n", app_init_match.end()) + 1
                content = content[:end_pos] + "\n" + preferred_scheme + "\n" + content[end_pos:]
            else:
                print(f"  Could not find Flask app initialization in {file_path}")
                return False
        
        changes_made = True
        print(f"  Added PREFERRED_URL_SCHEME = 'http' to {file_path}")
    
    # Fix session cookie settings
    cookie_changes = []
    cookie_settings = [
        ("SESSION_COOKIE_SECURE = True", "SESSION_COOKIE_SECURE = False"),
        ("SESSION_COOKIE_HTTPONLY = False", "SESSION_COOKIE_HTTPONLY = True"),
    ]
    
    for old, new in cookie_settings:
        if old in content:
            content = content.replace(old, new)
            cookie_changes.append(f"{old} -> {new}")
            changes_made = True
    
    if cookie_changes:
        print(f"  Updated cookie settings in {file_path}:")
        for change in cookie_changes:
            print(f"    {change}")
    
    # Check for and fix ProxyFix
    if "ProxyFix" not in content and "werkzeug.middleware.proxy_fix" not in content:
        proxy_import = "from werkzeug.middleware.proxy_fix import ProxyFix"
        proxy_setup = """
# Apply ProxyFix to handle forwarded headers correctly
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1
)
"""
        # Add import
        import_pos = content.find("import")
        if import_pos >= 0:
            # Find the end of import section
            import_end = import_pos
            while True:
                next_import = content.find("import", import_end + 6)
                if next_import < 0 or content[import_end:next_import].count("\n\n") > 0:
                    break
                import_end = next_import
            
            # Find the next double newline after imports
            next_section = content.find("\n\n", import_end)
            if next_section >= 0:
                content = content[:next_section] + "\n" + proxy_import + content[next_section:]
            else:
                content = content[:import_end] + "\n" + proxy_import + "\n" + content[import_end:]
            
            changes_made = True
            print(f"  Added ProxyFix import to {file_path}")
        
        # Add ProxyFix setup
        app_init_match = re.search(r"app\s*=\s*Flask\(.+\)", content)
        if app_init_match:
            end_pos = content.find("\n", app_init_match.end()) + 1
            content = content[:end_pos] + proxy_setup + content[end_pos:]
            changes_made = True
            print(f"  Added ProxyFix setup to {file_path}")
    
    # Make sure redirects use _scheme='http'
    redirect_changes = 0
    redirect_pattern = r'redirect\(url_for\([^)]+, _external=True[^)]*\)\)'
    for match in re.finditer(redirect_pattern, content):
        if '_scheme=' not in match.group(0):
            replacement = match.group(0).replace('_external=True', '_scheme=\'http\', _external=True')
            content = content[:match.start()] + replacement + content[match.end():]
            redirect_changes += 1
            changes_made = True
    
    if redirect_changes > 0:
        print(f"  Updated {redirect_changes} redirects to use _scheme='http'")
    
    # Save changes if any were made
    if changes_made:
        # Create backup
        backup_path = file_path + '.bak'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"  Created backup at {backup_path}")
        
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  Updated {file_path} successfully")
        return True
    else:
        print(f"  No changes needed for {file_path}")
        return False

def main():
    print("Flask Redirect Loop Fix Tool")
    print("--------------------------")
    
    flask_files = find_flask_app_files()
    if not flask_files:
        print("No Flask application files found.")
        sys.exit(1)
    
    print(f"Found {len(flask_files)} potential Flask application files:")
    for i, file in enumerate(flask_files, 1):
        print(f"{i}. {file}")
    
    if len(flask_files) == 1:
        target_file = flask_files[0]
    else:
        try:
            choice = int(input("\nWhich file would you like to fix? (enter number): "))
            target_file = flask_files[choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using the first file.")
            target_file = flask_files[0]
    
    print(f"\nAttempting to fix {target_file}...")
    if fix_flask_app(target_file):
        print("\nFix applied successfully!")
        print("\nRecommended actions:")
        print("1. Restart your Flask application")
        print("2. Clear browser cache")
        print("3. Try accessing your site again")
    else:
        print("\nNo changes were made. Your application may already be correctly configured.")

if __name__ == "__main__":
    main()