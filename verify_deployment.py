#!/usr/bin/env python3
"""
N1O1 Clinical Trials - Deployment Verification Script

This script verifies that your deployment is correctly handling URLs and redirects
on both Replit's internal deployment and custom domains.
"""
import os
import sys
import json
import argparse
from urllib.parse import urlparse
import requests

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

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
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    
    try:
        # Verify ping endpoint
        ping_url = f"{domain}/ping"
        print(f"Testing ping endpoint: {ping_url}")
        response = requests.get(ping_url, timeout=10)
        if response.status_code == 200 and response.text.strip() == "pong":
            print_success(f"Ping endpoint responded correctly: {response.text}")
        else:
            print_error(f"Ping endpoint response issue: {response.status_code} - {response.text}")
            return False
        
        # Verify health endpoint
        health_url = f"{domain}/system/health"
        print(f"Testing health endpoint: {health_url}")
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            try:
                health_data = response.json()
                print_success(f"Health endpoint responded with JSON: {json.dumps(health_data, indent=2)}")
            except json.JSONDecodeError:
                print_error(f"Health endpoint didn't return valid JSON: {response.text}")
                return False
        else:
            print_error(f"Health endpoint error: {response.status_code} - {response.text}")
            return False
        
        # Verify redirect handling
        print("Testing redirect handling (from /patient to /patients)...")
        redirects_session = requests.Session()
        redirect_url = f"{domain}/patient"
        response = redirects_session.get(redirect_url, timeout=10, allow_redirects=True)
        
        if response.url != redirect_url:
            print_success(f"Redirect worked: {redirect_url} → {response.url}")
        else:
            print_error(f"Redirect failed: Still at {redirect_url}")
            return False
        
        print_header("Deployment Verification SUCCESSFUL")
        print("Your application is correctly handling URLs and redirects.")
        print("It should work on both Replit's internal domain and custom domains.")
        return True
    
    except Exception as e:
        print_error(f"Verification failed: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Verify N1O1 Clinical Trials deployment")
    parser.add_argument("--domain", help="Domain to verify (e.g., 'https://example.com' or 'example.com')")
    args = parser.parse_args()
    
    if args.domain:
        domain = args.domain
    else:
        # Try to auto-detect domain
        replit_domain = os.environ.get("REPL_SLUG")
        if replit_domain:
            domain = f"https://{replit_domain}.repl.co"
            print(f"Using auto-detected Replit domain: {domain}")
        else:
            domain = "http://localhost:5000"
            print(f"Using default local domain: {domain}")
    
    print_header(f"Verifying N1O1 Clinical Trials deployment on: {domain}")
    success = verify_domain(domain)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())