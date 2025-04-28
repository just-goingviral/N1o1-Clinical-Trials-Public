#!/usr/bin/env python3
"""
N1O1 Clinical Trials - Deployment Diagnostics

This tool helps diagnose and fix deployment issues, particularly with custom domains.
It verifies URL generation, redirect handling, and environment configuration.
"""
import os
import sys
import json
import argparse
import re
import time
import platform
import socket
import ssl
import subprocess
from urllib.parse import urlparse, urljoin
from datetime import datetime

try:
    import requests
    from requests.exceptions import RequestException
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' module not found. Limited functionality available.")

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def print_subheader(text):
    """Print a formatted subheader"""
    print("\n" + "-" * 50)
    print(f" {text}")
    print("-" * 50)

def print_success(text):
    """Print a success message"""
    print(f"✓ {text}")

def print_warning(text):
    """Print a warning message"""
    print(f"⚠ {text}")

def print_error(text):
    """Print an error message"""
    print(f"✗ {text}")

def check_os_environment():
    """Check OS environment information"""
    print_subheader("Environment Information")
    
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Node.js version: {get_cmd_output('node --version')}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check environment variables
    env_vars = ['PORT', 'SERVER_NAME', 'PREFERRED_URL_SCHEME', 'FLASK_ENV', 'SESSION_COOKIE_SECURE']
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}={value}")
        else:
            print(f"  {var} not set")

def get_cmd_output(cmd):
    """Get output from a shell command"""
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

def check_network_connectivity(domain):
    """Check network connectivity to a domain"""
    print_subheader(f"Network Connectivity to {domain}")
    
    # Parse domain
    parsed = urlparse(domain)
    hostname = parsed.netloc or parsed.path
    
    # Remove port if present
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    # DNS lookup
    try:
        print(f"DNS lookup for {hostname}...")
        ip_addresses = socket.gethostbyname_ex(hostname)
        print_success(f"DNS Resolution: {ip_addresses}")
    except socket.gaierror as e:
        print_error(f"DNS lookup failed: {str(e)}")
    
    # Ping
    print(f"\nPinging {hostname}...")
    ping_param = "-n 3" if platform.system().lower() == "windows" else "-c 3"
    ping_result = get_cmd_output(f"ping {ping_param} {hostname}")
    print(ping_result)
    
    # Check HTTPS certificate if domain uses HTTPS
    if parsed.scheme == 'https' or not parsed.scheme:
        try:
            print(f"\nChecking SSL certificate for {hostname}...")
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract certificate information
                    subject = dict(x[0] for x in cert['subject'])
                    issued_to = subject.get('commonName', 'Unknown')
                    issuer = dict(x[0] for x in cert['issuer'])
                    issued_by = issuer.get('commonName', 'Unknown')
                    
                    print_success(f"SSL Certificate:")
                    print(f"  Issued to: {issued_to}")
                    print(f"  Issued by: {issued_by}")
                    print(f"  Valid from: {cert['notBefore']}")
                    print(f"  Valid until: {cert['notAfter']}")
        except Exception as e:
            print_warning(f"SSL certificate check failed: {str(e)}")

def check_url_generation(domain):
    """Verify URL generation from the application"""
    if not REQUESTS_AVAILABLE:
        print_warning("Skipping URL generation check: 'requests' module not available")
        return
    
    print_subheader("URL Generation Check")
    
    # Construct URL for health check
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    
    health_url = urljoin(domain, "/system/health")
    print(f"Testing health endpoint: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print_success(f"Health check succeeded with status {response.status_code}")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print_warning("Response is not valid JSON")
                print(f"Raw response: {response.text[:500]}")
        else:
            print_error(f"Health check failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except RequestException as e:
        print_error(f"Request failed: {str(e)}")

def check_redirect_handling(domain):
    """Check redirect handling in the application"""
    if not REQUESTS_AVAILABLE:
        print_warning("Skipping redirect check: 'requests' module not available")
        return
    
    print_subheader("Redirect Handling Check")
    
    # Construct URL for redirect test
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    
    redirect_url = urljoin(domain, "/patient")
    print(f"Testing redirect from: {redirect_url}")
    
    try:
        # First with redirects enabled
        session = requests.Session()
        response = session.get(redirect_url, timeout=10, allow_redirects=True)
        
        # Check if we were redirected
        if response.history:
            print_success(f"Redirect works! Path: {redirect_url} →")
            for i, resp in enumerate(response.history):
                print(f"  {i+1}. {resp.status_code}: {resp.url}")
            print(f"  Final: {response.status_code}: {response.url}")
        else:
            print_warning(f"No redirect occurred from {redirect_url}")
            
        # Then with redirects disabled to see the redirect details
        response = session.get(redirect_url, timeout=10, allow_redirects=False)
        if 300 <= response.status_code < 400:
            print_success(f"Redirect response: {response.status_code} {response.reason}")
            if 'Location' in response.headers:
                print(f"Location header: {response.headers['Location']}")
                
                # Analyze the redirect URL
                redirect_to = response.headers['Location']
                parsed = urlparse(redirect_to)
                
                if parsed.netloc:
                    print_success(f"Redirect uses absolute URL with domain: {parsed.netloc}")
                else:
                    print_warning(f"Redirect uses relative URL without domain. This may cause issues with custom domains.")
                    
                if parsed.scheme:
                    print(f"URL scheme: {parsed.scheme}")
                else:
                    print_warning("No URL scheme specified in redirect")
        else:
            print_error(f"No redirect response. Got {response.status_code} {response.reason}")
    except RequestException as e:
        print_error(f"Request failed: {str(e)}")

def check_proxy_headers():
    """Check proxy header handling in the application"""
    print_subheader("Proxy Header Configuration")
    
    main_file = "main.py"
    if not os.path.exists(main_file):
        print_error(f"Could not find {main_file}")
        return
    
    try:
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check for ProxyFix middleware
        proxy_pattern = r"ProxyFix\(.*\)"
        proxy_matches = re.findall(proxy_pattern, content, re.DOTALL)
        
        if proxy_matches:
            print_success("Found ProxyFix middleware configuration:")
            for match in proxy_matches:
                print(f"  {match.strip()}")
                
            # Check for x_proto parameter
            if "x_proto" in ''.join(proxy_matches):
                print_success("ProxyFix is configured to handle X-Forwarded-Proto headers")
            else:
                print_warning("ProxyFix may not be handling X-Forwarded-Proto headers correctly")
                
            # Check for x_host parameter
            if "x_host" in ''.join(proxy_matches):
                print_success("ProxyFix is configured to handle X-Forwarded-Host headers")
            else:
                print_warning("ProxyFix may not be handling X-Forwarded-Host headers correctly")
        else:
            print_warning("Could not find ProxyFix middleware configuration")
        
        # Check for safe_url_for implementation
        url_for_pattern = r"def safe_url_for\(.*?\).*?return url_for\(.*?\)"
        url_for_matches = re.findall(url_for_pattern, content, re.DOTALL)
        
        if url_for_matches:
            print_success("Found safe_url_for implementation:")
            
            # Check for X-Forwarded-Proto handling
            if "X-Forwarded-Proto" in ''.join(url_for_matches):
                print_success("safe_url_for handles X-Forwarded-Proto headers")
            else:
                print_warning("safe_url_for may not be respecting X-Forwarded-Proto headers")
        else:
            print_warning("Could not find safe_url_for implementation")
    
    except Exception as e:
        print_error(f"Error checking proxy configuration: {str(e)}")

def check_replit_environment():
    """Check if running in Replit environment"""
    print_subheader("Replit Environment")
    
    # Check for Replit-specific environment variables
    replit_vars = {
        'REPL_ID': os.environ.get('REPL_ID'),
        'REPL_OWNER': os.environ.get('REPL_OWNER'),
        'REPL_SLUG': os.environ.get('REPL_SLUG'),
        'REPLIT_DB_URL': os.environ.get('REPLIT_DB_URL'),
    }
    
    in_replit = any(replit_vars.values())
    
    if in_replit:
        print_success("Running in Replit environment")
        for key, value in replit_vars.items():
            if value:
                masked_value = value[:5] + '...' if key == 'REPLIT_DB_URL' and value else value
                print(f"  {key}={masked_value}")
        
        # Get Replit domain
        repl_slug = replit_vars['REPL_SLUG']
        repl_owner = replit_vars['REPL_OWNER']
        if repl_slug and repl_owner:
            print(f"Replit URL: https://{repl_slug}.{repl_owner}.repl.co")
    else:
        print("Not running in Replit environment")

def check_flask_environment():
    """Check Flask environment configuration"""
    print_subheader("Flask Environment Configuration")
    
    # Check main.py for Flask configuration
    main_file = "main.py"
    if not os.path.exists(main_file):
        print_error(f"Could not find {main_file}")
        return
    
    try:
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check cookie settings
        cookie_settings = {
            'SESSION_COOKIE_SECURE': re.search(r"SESSION_COOKIE_SECURE.*?=.*?(True|False)", content),
            'SERVER_NAME': re.search(r"SERVER_NAME.*?=.*?(None|'[^']*'|\"[^\"]*\")", content),
            'PREFERRED_URL_SCHEME': re.search(r"PREFERRED_URL_SCHEME.*?=.*?('[^']*'|\"[^\"]*\")", content),
            'SESSION_COOKIE_DOMAIN': re.search(r"SESSION_COOKIE_DOMAIN.*?=.*?(None|'[^']*'|\"[^\"]*\")", content),
        }
        
        print("Flask Configuration:")
        for setting, match in cookie_settings.items():
            if match:
                print(f"  {setting}: {match.group(1)}")
            else:
                print(f"  {setting}: Not found or using default")
        
        # Check for potentially problematic settings
        server_name_match = cookie_settings['SERVER_NAME']
        if server_name_match and 'None' not in server_name_match.group(1):
            print_warning(f"SERVER_NAME is set to {server_name_match.group(1)}. This can cause redirect issues with custom domains.")
        
        cookie_secure_match = cookie_settings['SESSION_COOKIE_SECURE']
        if cookie_secure_match and 'True' in cookie_secure_match.group(1):
            print_warning("SESSION_COOKIE_SECURE is True. This may cause issues if your site is not using HTTPS.")
        
        scheme_match = cookie_settings['PREFERRED_URL_SCHEME']
        if scheme_match and "'http'" in scheme_match.group(1):
            print_warning("PREFERRED_URL_SCHEME is hardcoded to 'http'. This may cause issues with HTTPS domains.")
        
    except Exception as e:
        print_error(f"Error checking Flask configuration: {str(e)}")

def check_route_files():
    """Check route files for URL generation issues"""
    print_subheader("Route Files Check")
    
    routes_dir = "routes"
    if not os.path.exists(routes_dir):
        print_error(f"Could not find routes directory: {routes_dir}")
        return
    
    # Patterns to look for
    patterns = {
        'hardcoded_scheme': (r"_scheme\s*=\s*'http'", "Hardcoded HTTP scheme"),
        'raw_redirect': (r"redirect\(url_for\(", "Direct redirect instead of safe_redirect"),
        'raw_url_for': (r"(?<!\w)url_for\((?!.*?safe_url_for)", "Direct url_for instead of safe_url_for"),
    }
    
    file_count = 0
    issue_count = 0
    issues_by_file = {}
    
    try:
        for root, _, files in os.walk(routes_dir):
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    file_count += 1
                    
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    file_issues = []
                    for pattern_name, (pattern, description) in patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            issue_count += len(matches)
                            file_issues.append(f"{description} ({len(matches)} instances)")
                    
                    if file_issues:
                        issues_by_file[file_path] = file_issues
        
        if issue_count > 0:
            print_warning(f"Found {issue_count} potential issues in {len(issues_by_file)} route files:")
            for file_path, issues in issues_by_file.items():
                print(f"\n  {os.path.basename(file_path)}:")
                for issue in issues:
                    print(f"    - {issue}")
            
            print("\nRecommendation: Run apply_deployment_fixes.py to fix these issues automatically")
        else:
            print_success(f"Checked {file_count} route files. No URL generation issues found.")
    
    except Exception as e:
        print_error(f"Error checking route files: {str(e)}")

def verify_domain(domain):
    """Verify a domain is properly configured"""
    if not REQUESTS_AVAILABLE:
        print_error("Cannot verify domain without 'requests' module")
        print("Install it with: pip install requests")
        return False
    
    print_header(f"Verifying N1O1 Clinical Trials deployment on: {domain}")
    
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    
    try:
        # Check OS and environment
        check_os_environment()
        
        # Check if running in Replit
        check_replit_environment()
        
        # Check network connectivity
        check_network_connectivity(domain)
        
        # Check Flask environment
        check_flask_environment()
        
        # Check proxy headers
        check_proxy_headers()
        
        # Check route files
        check_route_files()
        
        # Verify URL generation
        check_url_generation(domain)
        
        # Check redirect handling
        check_redirect_handling(domain)
        
        print_header("Deployment Verification Complete")
        print("Use these diagnostics to troubleshoot any deployment issues.")
        return True
    
    except Exception as e:
        print_error(f"Verification failed: {str(e)}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print_header("Installing Required Dependencies")
    
    try:
        import pip
        print("Installing 'requests' package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print_success("Dependencies installed successfully")
        print("Please run this script again to perform diagnostics")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Diagnose N1O1 Clinical Trials deployment issues")
    parser.add_argument("--domain", help="Domain to verify (e.g., 'https://example.com' or 'example.com')")
    parser.add_argument("--install-deps", action="store_true", help="Install required dependencies")
    args = parser.parse_args()
    
    if args.install_deps:
        return 0 if install_dependencies() else 1
    
    if not REQUESTS_AVAILABLE:
        print_warning("The 'requests' module is required for full diagnostics")
        print("Run: python deployment_diagnostics.py --install-deps")
    
    if args.domain:
        domain = args.domain
    else:
        # Try to auto-detect domain
        replit_slug = os.environ.get("REPL_SLUG")
        replit_owner = os.environ.get("REPL_OWNER")
        if replit_slug and replit_owner:
            domain = f"https://{replit_slug}.{replit_owner}.repl.co"
            print(f"Using auto-detected Replit domain: {domain}")
        else:
            domain = "http://localhost:5000"
            print(f"Using default local domain: {domain}")
    
    success = verify_domain(domain)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())