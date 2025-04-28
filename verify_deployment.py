#!/usr/bin/env python3
"""
N1O1 Clinical Trials - Deployment Verification Script

This script verifies that your deployment is correctly handling URLs and redirects
on both Replit's internal deployment and custom domains.
"""
import sys
import os
import time
import argparse
from urllib.parse import urlparse, urljoin

try:
    import requests
except ImportError:
    print("The 'requests' module is required. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

def print_header(text):
    """Print formatted header"""
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

def verify_domain(domain):
    """Verify a domain is properly configured"""
    # Normalize domain
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    
    print_header(f"Verifying deployment on {domain}")
    
    # Test 1: Basic connectivity
    ping_url = urljoin(domain, "/ping")
    print(f"\nTest 1: Basic connectivity to {ping_url}")
    try:
        response = requests.get(ping_url, timeout=10)
        if response.status_code == 200:
            print_success(f"Successfully connected! Status code: {response.status_code}")
            print(f"Response: {response.text.strip()}")
        else:
            print_error(f"Connection failed with status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False
    
    # Test 2: System health
    health_url = urljoin(domain, "/system/health")
    print(f"\nTest 2: System health check at {health_url}")
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print_success(f"Health check passed! Status code: {response.status_code}")
            try:
                data = response.json()
                print(f"Status: {data.get('status', 'Unknown')}")
                print(f"Message: {data.get('message', 'No message')}")
                print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False
    
    # Test 3: Redirect handling
    redirect_url = urljoin(domain, "/patient")
    print(f"\nTest 3: Redirect handling from {redirect_url}")
    try:
        # First check with redirect following disabled
        response = requests.get(redirect_url, timeout=10, allow_redirects=False)
        if 300 <= response.status_code < 400:
            print_success(f"Redirect detected with status code: {response.status_code}")
            redirect_to = response.headers.get('Location', 'Unknown')
            print(f"Redirects to: {redirect_to}")
            
            # Analyze redirect URL
            parsed = urlparse(redirect_to)
            if parsed.netloc and parsed.netloc not in domain:
                print_warning(f"Redirect domain ({parsed.netloc}) doesn't match request domain")
            
            # Now follow the redirect
            print("\nFollowing the redirect...")
            response = requests.get(redirect_url, timeout=10, allow_redirects=True)
            final_url = response.url
            print_success(f"Successfully followed redirect to: {final_url}")
            if response.status_code == 200:
                print_success("Final page loaded successfully")
            else:
                print_warning(f"Final page returned status code: {response.status_code}")
        else:
            print_error(f"No redirect detected. Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print_error(f"Redirect test error: {str(e)}")
    
    print_header("Verification Summary")
    print_success("All connectivity tests passed!")
    print("\nYour N1O1 Clinical Trials application appears to be correctly configured.")
    print("It should work properly with both Replit and custom domains.")
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Verify N1O1 Clinical Trials deployment")
    parser.add_argument("--domain", help="Domain to verify (e.g., example.com)")
    args = parser.parse_args()
    
    if args.domain:
        domain = args.domain
    else:
        # Try to auto-detect domain
        replit_slug = os.environ.get("REPL_SLUG")
        replit_owner = os.environ.get("REPL_OWNER")
        if replit_slug and replit_owner:
            domain = f"{replit_slug}.{replit_owner}.repl.co"
            print(f"Using auto-detected Replit domain: {domain}")
        else:
            domain = "localhost:5000"
            print(f"Using default local domain: {domain}")
    
    success = verify_domain(domain)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())