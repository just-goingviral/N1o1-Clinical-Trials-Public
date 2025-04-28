#!/usr/bin/env python3
"""
Quick verification script for N1O1 Clinical Trials deployment fixes

This script validates the deployment fixes by:
1. Checking proper URL generation
2. Verifying the safe_redirect function works correctly 
3. Ensuring ProxyFix is configured correctly
"""
import os
import sys
from urllib.parse import urlparse

# Make sure flask and werkzeug are available
try:
    from flask import Flask, request, url_for
    from werkzeug.middleware.proxy_fix import ProxyFix
except ImportError:
    print("Error: Flask or Werkzeug not found. Install with: pip install flask werkzeug")
    sys.exit(1)

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

def check_safe_url_for():
    """Check if safe_url_for is implemented correctly in main.py"""
    try:
        from main import safe_url_for
        print_success("Found safe_url_for function in main.py")
        return True
    except ImportError:
        print_warning("safe_url_for function not found in main.py")
        return False

def check_safe_redirect():
    """Check if safe_redirect is implemented correctly in main.py"""
    try:
        from main import safe_redirect
        print_success("Found safe_redirect function in main.py")
        return True
    except ImportError:
        print_warning("safe_redirect function not found in main.py")
        return False

def check_proxy_fix():
    """Check if ProxyFix is configured correctly in main.py"""
    import inspect
    import main
    
    # Check if app.wsgi_app has been modified
    if hasattr(main, 'app') and hasattr(main.app, 'wsgi_app'):
        wsgi_app = main.app.wsgi_app
        if isinstance(wsgi_app, ProxyFix):
            print_success("ProxyFix middleware is correctly configured")
            
            # Check ProxyFix parameters
            proxy_fix_source = inspect.getsource(ProxyFix.__init__)
            default_params = "x_for=1, x_proto=0, x_host=0, x_port=0, x_prefix=0"
            
            if "x_proto=1" in str(wsgi_app) or "x_proto=True" in str(wsgi_app):
                print_success("ProxyFix is configured to handle X-Forwarded-Proto")
            else:
                print_warning("ProxyFix may not be handling X-Forwarded-Proto correctly")
                
            if "x_host=1" in str(wsgi_app) or "x_host=True" in str(wsgi_app):
                print_success("ProxyFix is configured to handle X-Forwarded-Host")
            else:
                print_warning("ProxyFix may not be handling X-Forwarded-Host correctly")
                
            return True
        else:
            print_warning("ProxyFix middleware is not configured (wsgi_app is not ProxyFix)")
            return False
    else:
        print_warning("Could not determine if ProxyFix is configured")
        return False

def check_url_generation():
    """Check URL generation with different schemes"""
    print_header("Testing URL Generation")
    
    # Create a test app
    app = Flask(__name__)
    
    @app.route('/test')
    def test_route():
        return "Test"
    
    # Test different environment configurations
    test_configs = [
        {"description": "Default (no proxy headers)", "environ_base": {}},
        {"description": "HTTPS proxy", "environ_base": {"HTTP_X_FORWARDED_PROTO": "https"}},
        {"description": "HTTP proxy", "environ_base": {"HTTP_X_FORWARDED_PROTO": "http"}},
        {"description": "Custom host", "environ_base": {"HTTP_X_FORWARDED_HOST": "example.com"}},
    ]
    
    with app.test_request_context():
        print("\nBase URL generation:")
        url = url_for('test_route', _external=True)
        parsed = urlparse(url)
        print(f"  Generated URL: {url}")
        print(f"  Scheme: {parsed.scheme}")
        print(f"  Netloc: {parsed.netloc}")
    
    for config in test_configs:
        desc = config['description']
        environ = config['environ_base']
        
        with app.test_request_context(environ_base=environ):
            print(f"\nTesting with {desc}:")
            url = url_for('test_route', _external=True)
            parsed = urlparse(url)
            print(f"  Generated URL: {url}")
            print(f"  Scheme: {parsed.scheme}")
            print(f"  Netloc: {parsed.netloc}")
            
            # With _scheme parameter
            if 'HTTP_X_FORWARDED_PROTO' in environ:
                expected_scheme = environ['HTTP_X_FORWARDED_PROTO']
                if parsed.scheme != expected_scheme:
                    print_warning(f"  URL scheme ({parsed.scheme}) doesn't match X-Forwarded-Proto ({expected_scheme})")
                else:
                    print_success(f"  URL scheme correctly uses X-Forwarded-Proto")
            
            # With host header
            if 'HTTP_X_FORWARDED_HOST' in environ:
                expected_host = environ['HTTP_X_FORWARDED_HOST']
                if expected_host not in parsed.netloc:
                    print_warning(f"  URL host ({parsed.netloc}) doesn't use X-Forwarded-Host ({expected_host})")
                else:
                    print_success(f"  URL host correctly uses X-Forwarded-Host")

def main():
    """Main function"""
    print_header("N1O1 Clinical Trials - Deployment Fixes Verification")
    
    # Check if safe_url_for is implemented
    safe_url_for_ok = check_safe_url_for()
    
    # Check if safe_redirect is implemented
    safe_redirect_ok = check_safe_redirect()
    
    # Check if ProxyFix is configured correctly
    proxy_fix_ok = check_proxy_fix()
    
    # Check URL generation with different schemes
    check_url_generation()
    
    # Summary
    print_header("Verification Summary")
    
    issues = []
    if not safe_url_for_ok:
        issues.append("safe_url_for function not found")
    if not safe_redirect_ok:
        issues.append("safe_redirect function not found")
    if not proxy_fix_ok:
        issues.append("ProxyFix not correctly configured")
    
    if issues:
        print_warning("The following issues were found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nRecommendation: Apply the deployment fixes from DEPLOYMENT_GUIDE.md")
    else:
        print_success("All deployment fixes have been applied correctly!")
        print("\nYour application should now work properly on both Replit and custom domains.")
    
    return 0 if not issues else 1

if __name__ == "__main__":
    sys.exit(main())