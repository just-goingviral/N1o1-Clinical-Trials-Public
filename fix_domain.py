#!/usr/bin/env python3
"""
Fix custom domain configuration issues
This script diagnoses and fixes common issues with custom domains in Flask applications
"""
import os
import sys
import logging
import socket
import ssl
import requests
import time
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_replit_domain():
    """Get the Replit domain for this application"""
    try:
        repl_slug = os.environ.get('REPL_SLUG', 'unknown')
        repl_owner = os.environ.get('REPL_OWNER', 'unknown')
        replit_domain = f"https://{repl_slug}.{repl_owner}.repl.co"
        
        logger.info(f"Detected Replit domain: {replit_domain}")
        return replit_domain
    except Exception as e:
        logger.error(f"Error getting Replit domain: {e}")
        return None

def check_domain_info(domain):
    """Check if a domain is resolving properly"""
    domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
    
    logger.info(f"Checking DNS for domain: {domain}")
    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        logger.info(f"Domain {domain} resolves to: {', '.join(ip_addresses)}")
        return True, ip_addresses
    except socket.gaierror as e:
        logger.error(f"DNS lookup failed for {domain}: {e}")
        return False, None

def check_http_endpoint(url, endpoint="/ping"):
    """Check if an HTTP endpoint is accessible"""
    try:
        full_url = url.rstrip('/') + endpoint
        logger.info(f"Checking HTTP endpoint: {full_url}")
        
        response = requests.get(full_url, timeout=10)
        if response.status_code == 200:
            logger.info(f"Endpoint {full_url} is accessible (HTTP {response.status_code})")
            return True
        else:
            logger.warning(f"Endpoint {full_url} returned HTTP {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Error accessing {url}: {e}")
        return False

def check_https_cert(domain):
    """Check HTTPS certificate for a domain"""
    domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
    
    try:
        logger.info(f"Checking HTTPS certificate for: {domain}")
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert['issuer'])
                subject = dict(x[0] for x in cert['subject'])
                
                logger.info(f"Certificate issuer: {issuer.get('organizationName', 'Unknown')}")
                logger.info(f"Certificate subject: {subject.get('commonName', 'Unknown')}")
                return True
    except Exception as e:
        logger.error(f"HTTPS certificate check failed for {domain}: {e}")
        return False

def check_redirect_issue(url):
    """Check for redirect issues with a URL"""
    try:
        logger.info(f"Checking for redirect issues with: {url}")
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        if 300 <= response.status_code < 400:
            location = response.headers.get('Location', 'Unknown')
            logger.warning(f"Redirect detected: {url} -> {location} (HTTP {response.status_code})")
            return True, location
        else:
            logger.info(f"No redirect detected for {url} (HTTP {response.status_code})")
            return False, None
    except requests.RequestException as e:
        logger.error(f"Error checking redirects for {url}: {e}")
        return False, None

def fix_csrf_config():
    """Fix CSRF configuration in config.py or main.py"""
    try:
        csrf_config_found = False
        for filename in ['main.py', 'app.py', 'config.py']:
            if not os.path.exists(filename):
                continue
                
            with open(filename, 'r') as f:
                content = f.read()
            
            if 'WTF_CSRF_ENABLED' in content:
                csrf_config_found = True
                logger.info(f"CSRF configuration found in {filename}")
                
                # Fix CSRF configuration
                if "WTF_CSRF_CHECK_DEFAULT = False" not in content:
                    logger.info(f"Adding WTF_CSRF_CHECK_DEFAULT = False to {filename}")
                    # Look for the WTF_CSRF_ENABLED line
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'WTF_CSRF_ENABLED' in line:
                            # Insert the new config after this line
                            lines.insert(i+1, "app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable CSRF checks for redirects")
                            break
                    
                    # Write the updated content
                    with open(filename, 'w') as f:
                        f.write('\n'.join(lines))
                    logger.info(f"Updated CSRF configuration in {filename}")
        
        if not csrf_config_found:
            logger.warning("No CSRF configuration found in any config files")
    except Exception as e:
        logger.error(f"Error fixing CSRF configuration: {e}")

def fix_session_config():
    """Fix session configuration in config.py or main.py"""
    try:
        session_config_found = False
        for filename in ['main.py', 'app.py', 'config.py']:
            if not os.path.exists(filename):
                continue
                
            with open(filename, 'r') as f:
                content = f.read()
            
            if 'SESSION_TYPE' in content:
                session_config_found = True
                logger.info(f"Session configuration found in {filename}")
                
                # Look for session cookie domain config and fix if needed
                if "SESSION_COOKIE_DOMAIN" not in content:
                    logger.info(f"Adding SESSION_COOKIE_DOMAIN = None to {filename}")
                    
                    # Look for the SESSION_TYPE line or similar
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'SESSION_TYPE' in line:
                            # Insert cookie configs after this line
                            insert_index = i+1
                            while insert_index < len(lines) and ('SESSION_' in lines[insert_index] or lines[insert_index].strip() == ''):
                                insert_index += 1
                                
                            session_cookie_config = [
                                "app.config['SESSION_COOKIE_SECURE'] = False  # Allow cookies over HTTP for development",
                                "app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies",
                                "app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same site",
                                "app.config['SESSION_COOKIE_PATH'] = '/'  # Set cookie path to root",
                                "app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow the browser to set domain automatically"
                            ]
                            
                            for config_line in reversed(session_cookie_config):
                                lines.insert(insert_index, config_line)
                            
                            break
                    
                    # Write the updated content
                    with open(filename, 'w') as f:
                        f.write('\n'.join(lines))
                    logger.info(f"Updated session configuration in {filename}")
        
        if not session_config_found:
            logger.warning("No session configuration found in any config files")
    except Exception as e:
        logger.error(f"Error fixing session configuration: {e}")

def fix_proxy_config():
    """Fix proxy configuration in main.py or app.py"""
    try:
        proxy_config_found = False
        for filename in ['main.py', 'app.py']:
            if not os.path.exists(filename):
                continue
                
            with open(filename, 'r') as f:
                content = f.read()
            
            # Check if ProxyFix is already imported
            proxy_fix_imported = 'ProxyFix' in content
            proxy_fix_applied = 'app.wsgi_app = ProxyFix' in content
            
            if proxy_fix_applied:
                proxy_config_found = True
                logger.info(f"ProxyFix already applied in {filename}")
                continue
                
            # Look for 'from flask import Flask' line
            lines = content.split('\n')
            flask_import_idx = -1
            app_creation_idx = -1
            
            for i, line in enumerate(lines):
                if 'from flask import' in line and 'Flask' in line:
                    flask_import_idx = i
                elif 'app = Flask' in line:
                    app_creation_idx = i
            
            if flask_import_idx >= 0 and app_creation_idx >= 0:
                logger.info(f"Found Flask app creation in {filename}")
                
                # Add ProxyFix import if needed
                if not proxy_fix_imported:
                    logger.info(f"Adding ProxyFix import to {filename}")
                    import_line = "from werkzeug.middleware.proxy_fix import ProxyFix"
                    # Insert after the flask import
                    lines.insert(flask_import_idx + 1, import_line)
                    # Update app_creation_idx since we inserted a line
                    app_creation_idx += 1
                
                # Add ProxyFix middleware
                logger.info(f"Adding ProxyFix middleware to {filename}")
                proxy_config = [
                    "",
                    "# Apply ProxyFix to handle forwarded headers from proxy servers",
                    "# This is important for correct URL generation with custom domains and HTTPS",
                    "app.wsgi_app = ProxyFix(",
                    "    app.wsgi_app,",
                    "    x_for=1,      # Number of trusted proxies for X-Forwarded-For",
                    "    x_proto=1,    # Number of trusted proxies for X-Forwarded-Proto",
                    "    x_host=1,     # Number of trusted proxies for X-Forwarded-Host",
                    "    x_port=1,     # Number of trusted proxies for X-Forwarded-Port",
                    "    x_prefix=1    # Number of trusted proxies for X-Forwarded-Prefix",
                    ")"
                ]
                
                # Insert after app creation
                for i, config_line in enumerate(proxy_config):
                    lines.insert(app_creation_idx + 1 + i, config_line)
                
                # Write the updated content
                with open(filename, 'w') as f:
                    f.write('\n'.join(lines))
                logger.info(f"Updated proxy configuration in {filename}")
                proxy_config_found = True
        
        if not proxy_config_found:
            logger.warning("Could not find appropriate location to add ProxyFix in any files")
    except Exception as e:
        logger.error(f"Error fixing proxy configuration: {e}")

def fix_redirects():
    """Fix redirect issues in routes"""
    redirect_count = 0
    try:
        for root, dirs, files in os.walk('.'):
            # Skip directories that typically don't contain route files
            if any(skip_dir in root for skip_dir in ['.git', 'venv', 'node_modules', '__pycache__']):
                continue
                
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Look for redirect to url_for without _external=True
                if 'redirect(' in content and 'url_for(' in content and '_external=True' not in content:
                    logger.info(f"Found possible redirect issue in {file_path}")
                    
                    lines = content.split('\n')
                    modified = False
                    
                    for i, line in enumerate(lines):
                        if 'redirect(' in line and 'url_for(' in line and '_external=True' not in line:
                            # Very simple check - might need improvement for complex code
                            if line.strip().startswith('return') and 'redirect' in line:
                                # Replace url_for( with url_for( ... , _external=True)
                                original_line = line
                                # Simple case: url_for('endpoint')
                                if "url_for('" in line and ")" in line:
                                    before, after = line.split("url_for('", 1)
                                    endpoint, rest = after.split("'", 1)
                                    if ")" in rest:
                                        param_close = rest.find(")")
                                        if param_close >= 0:
                                            if rest[:param_close].strip() and not rest[:param_close].strip().endswith(","):
                                                # Has parameters, add comma
                                                lines[i] = before + "url_for('" + endpoint + "'" + rest[:param_close] + ", _external=True" + rest[param_close:]
                                            else:
                                                # No parameters or already has comma
                                                lines[i] = before + "url_for('" + endpoint + "'" + rest[:param_close] + " _external=True" + rest[param_close:]
                                            modified = True
                                            redirect_count += 1
                                            logger.info(f"Fixed redirect in {file_path}:{i+1}")
                                            logger.info(f"  Before: {original_line.strip()}")
                                            logger.info(f"  After:  {lines[i].strip()}")
                    
                    if modified:
                        with open(file_path, 'w') as f:
                            f.write('\n'.join(lines))
                        logger.info(f"Updated redirects in {file_path}")
        
        logger.info(f"Fixed {redirect_count} redirects in total")
    except Exception as e:
        logger.error(f"Error fixing redirects: {e}")

def clear_session_files():
    """Clear session files to reset sessions"""
    try:
        session_dir = os.path.join(os.path.dirname(__file__), 'flask_session')
        if os.path.exists(session_dir):
            logger.info(f"Clearing session files from {session_dir}")
            count = 0
            for file in os.listdir(session_dir):
                file_path = os.path.join(session_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            logger.info(f"Cleared {count} session files")
        else:
            logger.warning(f"Session directory {session_dir} does not exist")
    except Exception as e:
        logger.error(f"Error clearing session files: {e}")

def main():
    """Main function"""
    logger.info("Starting custom domain fix utility")
    
    # Check replit domain
    replit_domain = check_replit_domain()
    
    # Fix domain-related issues
    logger.info("Fixing domain-related issues...")
    
    # Fix proxy configuration
    logger.info("Fixing proxy configuration...")
    fix_proxy_config()
    
    # Fix session configuration
    logger.info("Fixing session configuration...")
    fix_session_config()
    
    # Fix CSRF configuration
    logger.info("Fixing CSRF configuration...")
    fix_csrf_config()
    
    # Fix redirects
    logger.info("Fixing redirects...")
    fix_redirects()
    
    # Clear session files
    logger.info("Clearing session files...")
    clear_session_files()
    
    logger.info("Domain fix utility completed")
    logger.info("Please restart your application for changes to take effect")

if __name__ == "__main__":
    main()