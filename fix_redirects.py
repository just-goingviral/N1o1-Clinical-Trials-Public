"""
Fix redirect loops in Flask applications

This script addresses the common causes of redirect loops in Flask applications,
especially when running behind a proxy or with custom domains.

Usage: python fix_redirects.py
"""

import os
import re
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print a success message"""
    print(f"✓ {text}")

def print_warning(text):
    """Print a warning message"""
    print(f"⚠ {text}")

def fix_session_settings():
    """Fix session settings in main.py"""
    main_py = Path("main.py")
    
    if not main_py.exists():
        print_warning("main.py not found. Skipping session settings fix.")
        return
    
    content = main_py.read_text()
    fixed_content = content
    
    # Fix 1: Ensure SESSION_COOKIE_SECURE is properly set
    if "SESSION_COOKIE_SECURE" in content:
        fixed_content = re.sub(
            r"app\.config\['SESSION_COOKIE_SECURE'\]\s*=\s*.*",
            "app.config['SESSION_COOKIE_SECURE'] = False  # Set to False to avoid redirect loops",
            fixed_content
        )
    else:
        # Add session cookie settings if they don't exist
        secure_cookie_setting = "\n# Fix for redirect loops\napp.config['SESSION_COOKIE_SECURE'] = False"
        
        # Find a good place to insert it (after other app.config settings)
        if "app.config" in fixed_content:
            insertion_point = fixed_content.rfind("app.config")
            insertion_point = fixed_content.find("\n", insertion_point) + 1
            fixed_content = fixed_content[:insertion_point] + secure_cookie_setting + fixed_content[insertion_point:]
        else:
            fixed_content += "\n" + secure_cookie_setting
    
    # Fix 2: Ensure the application sets PREFERRED_URL_SCHEME
    if "PREFERRED_URL_SCHEME" not in fixed_content:
        scheme_setting = "\n# Fix for custom domain handling\napp.config['PREFERRED_URL_SCHEME'] = 'http'"
        
        # Insert after SESSION_COOKIE_SECURE
        if "SESSION_COOKIE_SECURE" in fixed_content:
            insertion_point = fixed_content.find("SESSION_COOKIE_SECURE")
            insertion_point = fixed_content.find("\n", insertion_point) + 1
            fixed_content = fixed_content[:insertion_point] + scheme_setting + fixed_content[insertion_point:]
        # Or after app creation
        elif "app = Flask" in fixed_content:
            insertion_point = fixed_content.find("app = Flask")
            insertion_point = fixed_content.find("\n", insertion_point) + 1
            fixed_content = fixed_content[:insertion_point] + scheme_setting + fixed_content[insertion_point:]
        else:
            fixed_content += "\n" + scheme_setting
    
    # Fix 3: Ensure that url_for calls consistently use _scheme parameter
    def add_scheme_to_url_for(match):
        # Check if _scheme is already in the URL
        if "_scheme=" in match.group(0):
            return match.group(0)
        # Check if _external=True is in the URL
        elif "_external=True" in match.group(0) or "_external = True" in match.group(0):
            # Return with _scheme added before the closing parenthesis
            return match.group(0).replace(")", ", _scheme='http')")
        else:
            # Not an external URL, leave as is
            return match.group(0)
    
    fixed_content = re.sub(r'url_for\([^)]*\)', add_scheme_to_url_for, fixed_content)
    
    # Fix 4: Add a safer redirect function
    if "def safe_redirect(" not in fixed_content:
        safe_redirect_function = """
# Safe redirect helper to prevent redirect loops
def safe_redirect(endpoint, **kwargs):
    # Force HTTP scheme to prevent HTTPS->HTTP->HTTPS loops
    kwargs.setdefault('_scheme', 'http')
    kwargs.setdefault('_external', True)
    return redirect(url_for(endpoint, **kwargs))
"""
        # Add after imports
        if "import redirect" in fixed_content or "from flask import redirect" in fixed_content:
            fixed_content = fixed_content + "\n" + safe_redirect_function
        # Try after the Flask app creation
        elif "app = Flask" in fixed_content:
            insertion_point = fixed_content.find("app = Flask")
            insertion_point = fixed_content.find("\n", insertion_point) + 1
            fixed_content = fixed_content[:insertion_point] + safe_redirect_function + fixed_content[insertion_point:]
        else:
            # Add to the end
            fixed_content += "\n" + safe_redirect_function
    
    # Write back only if there were changes
    if fixed_content != content:
        main_py.write_text(fixed_content)
        print_success("Updated session settings in main.py")
    else:
        print_success("Session settings already correctly configured")

def fix_proxy_settings():
    """Fix proxy settings in main.py"""
    main_py = Path("main.py")
    
    if not main_py.exists():
        print_warning("main.py not found. Skipping proxy settings fix.")
        return
    
    content = main_py.read_text()
    fixed_content = content
    
    # Check for ProxyFix middleware
    if "ProxyFix" not in content:
        proxy_fix_import = "from werkzeug.middleware.proxy_fix import ProxyFix"
        proxy_fix_config = """
# Apply ProxyFix middleware to handle proxied requests correctly
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # Number of trusted proxies for X-Forwarded-For
    x_proto=1,    # Number of trusted proxies for X-Forwarded-Proto 
    x_host=1,     # Number of trusted proxies for X-Forwarded-Host
    x_port=1      # Number of trusted proxies for X-Forwarded-Port
)"""
        
        # Add the import
        if "from flask import" in content:
            insertion_point = content.find("from flask import")
            insertion_point = content.find("\n", insertion_point) + 1
            fixed_content = fixed_content[:insertion_point] + proxy_fix_import + "\n" + fixed_content[insertion_point:]
        else:
            # Add at the top after any other imports
            import_section_end = 0
            for line in content.split("\n"):
                if line.startswith("import ") or line.startswith("from "):
                    potential_end = content.find(line) + len(line) + 1
                    if potential_end > import_section_end:
                        import_section_end = potential_end
            
            if import_section_end > 0:
                fixed_content = fixed_content[:import_section_end] + "\n" + proxy_fix_import + fixed_content[import_section_end:]
            else:
                # No imports found, add at the top
                fixed_content = proxy_fix_import + "\n" + fixed_content
        
        # Add the ProxyFix configuration right after app creation
        if "app = Flask" in fixed_content:
            insertion_point = fixed_content.find("app = Flask")
            insertion_point = fixed_content.find("\n", insertion_point) + 1
            fixed_content = fixed_content[:insertion_point] + proxy_fix_config + fixed_content[insertion_point:]
        else:
            # Add near the top if we can't find app creation
            fixed_content = fixed_content.split("\n", 1)[0] + "\n" + proxy_fix_config + "\n" + fixed_content.split("\n", 1)[1]
    
    # Write back only if there were changes
    if fixed_content != content:
        main_py.write_text(fixed_content)
        print_success("Added ProxyFix middleware configuration")
    else:
        print_success("ProxyFix middleware already correctly configured")

def fix_login_redirects():
    """Fix Flask-Login redirect issues"""
    main_py = Path("main.py")
    
    if not main_py.exists():
        print_warning("main.py not found. Skipping login redirect fix.")
        return
    
    content = main_py.read_text()
    fixed_content = content
    
    # Check for login_manager configuration
    if "login_manager" in content and "login_view" in content:
        # Add a safety net for login redirects
        login_next_fix = """
# Override Flask-Login's unauthorized handler to apply our scheme fixes
@login_manager.unauthorized_handler
def unauthorized():
    # Handle unauthorized access attempts with scheme-aware redirects
    # Get the login URL with the next parameter correctly set
    login_url = url_for(
        login_manager.login_view,
        next=request.path if request.path != "/" else None,
        _scheme='http',  # Force HTTP scheme
        _external=True
    )
    return redirect(login_url)
"""
        
        # Insert after login_manager configuration
        if "login_manager.login_view" in fixed_content:
            insertion_point = fixed_content.find("login_manager.login_view")
            # Find next paragraph after this point
            paragraph_end = fixed_content.find("\n\n", insertion_point)
            if paragraph_end > 0:
                fixed_content = fixed_content[:paragraph_end+2] + login_next_fix + fixed_content[paragraph_end+2:]
            else:
                # No paragraph break found, add at the end of the file
                fixed_content += "\n" + login_next_fix
        
        # Write back only if there were changes
        if fixed_content != content:
            main_py.write_text(fixed_content)
            print_success("Fixed Flask-Login redirect handling")
        else:
            print_success("Flask-Login redirect handling already correctly configured")
    else:
        print_warning("No Flask-Login configuration found. Skipping login redirect fix.")

def apply_fixes():
    """Apply all redirect fixes"""
    print_header("Fixing Redirect Loops")
    
    # Apply session setting fixes
    print("\n>> Updating session settings...")
    fix_session_settings()
    
    # Apply proxy fixes
    print("\n>> Configuring proxy middleware...")
    fix_proxy_settings()
    
    # Apply login redirect fixes
    print("\n>> Fixing login redirects...")
    fix_login_redirects()
    
    print("\n>> Done! All fixes applied.")
    print("\nReminder: You'll need to restart your application for these changes to take effect.")

if __name__ == "__main__":
    apply_fixes()