
#!/usr/bin/env python
"""
Check custom domain configuration and connectivity
"""
import os
import sys
import time
import socket
import requests
import subprocess
import json
from urllib.parse import urlparse

def check_dns(domain):
    """Check DNS resolution for a domain"""
    print(f"\n🔍 Checking DNS resolution for {domain}...")
    try:
        # Get IP address from domain
        ip_address = socket.gethostbyname(domain)
        print(f"✅ DNS resolution successful: {domain} resolves to {ip_address}")
        return ip_address
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed for {domain}: {str(e)}")
        return None

def check_replit_domain():
    """Get the Replit domain for this application"""
    try:
        with open('.replit', 'r') as f:
            for line in f:
                if 'deploymentTarget' in line:
                    print("✅ Found deployment configuration in .replit")
                    return True
    except Exception as e:
        print(f"❌ Error reading .replit file: {str(e)}")
    
    return False

def check_http_endpoint(url, endpoint="/system/health"):
    """Check if an HTTP endpoint is accessible"""
    full_url = f"{url.rstrip('/')}{endpoint}"
    print(f"\n🔍 Checking HTTP endpoint: {full_url}")
    try:
        response = requests.get(full_url, timeout=10)
        print(f"✅ HTTP request successful: Status code {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
                return True
            except:
                print(f"Response text: {response.text[:100]}...")
                return True
        return False
    except requests.RequestException as e:
        print(f"❌ HTTP request failed: {str(e)}")
        return False

def suggest_fixes(domain):
    """Suggest possible fixes based on diagnosis"""
    print("\n🔧 Suggested fixes:")
    
    # Check if domain has proper DNS records
    print("\n1. Verify DNS Configuration:")
    print("   - Ensure your domain has an A record pointing to Replit's IP")
    print("   - Ensure your domain has a TXT record for verification")
    print("   - These records should be configured in your domain registrar (like Cloudflare, Namecheap, etc.)")
    
    # Check deployment configuration
    print("\n2. Verify Replit Deployment Configuration:")
    print("   - Go to the Deployments tab in Replit")
    print("   - Check that your custom domain is properly linked")
    print("   - Ensure the verification status is 'Verified'")
    
    # Check for port configuration issues
    print("\n3. Check Port Configuration:")
    print("   - Make sure your application is using the PORT environment variable")
    print("   - Confirm that run.sh or Procfile is using $PORT instead of hardcoded values")
    
    # Suggest redeployment
    print("\n4. Try Redeploying:")
    print("   - Go to the Deployments tab in Replit")
    print("   - Click 'Redeploy'")
    
    print("\n5. Fix any SSL/HTTPS issues:")
    print("   - Replit handles SSL certificates automatically")
    print("   - Make sure that your domain registrar is not using its own SSL (like Cloudflare proxy)")
    
    print("\nRun ./fix_domain.sh to apply automatic fixes for port configuration issues.")

def main():
    """Main function to check domain configuration"""
    print("N1O1 Clinical Trials - Domain Configuration Check")
    print("================================================")
    
    # Check if domain argument provided
    if len(sys.argv) > 1:
        custom_domain = sys.argv[1]
    else:
        custom_domain = input("Enter your custom domain (e.g., trials.n1o1app.com): ")
    
    # Check if domain is properly formatted
    if not custom_domain.startswith(('http://', 'https://')):
        custom_domain_url = f"https://{custom_domain}"
    else:
        custom_domain_url = custom_domain
        custom_domain = urlparse(custom_domain).netloc
    
    # Get Replit domain
    replit_domain = "drnathanbryan.replit.app"  # Default
    
    # Print the domains we're checking
    print(f"\nChecking custom domain: {custom_domain}")
    print(f"Comparing to Replit domain: {replit_domain}")
    
    # Check DNS resolution
    custom_ip = check_dns(custom_domain)
    replit_ip = check_dns(replit_domain)
    
    # Check environment configuration
    has_deployment_config = check_replit_domain()
    
    # Check HTTP endpoints
    replit_http_works = check_http_endpoint(f"https://{replit_domain}")
    custom_http_works = check_http_endpoint(custom_domain_url)
    
    # Print summary
    print("\n=== Diagnosis Summary ===")
    print(f"Custom domain DNS resolution: {'✅ Working' if custom_ip else '❌ Failed'}")
    print(f"Replit domain DNS resolution: {'✅ Working' if replit_ip else '❌ Failed'}")
    print(f"Deployment configuration: {'✅ Found' if has_deployment_config else '❌ Not found'}")
    print(f"Replit domain HTTP: {'✅ Working' if replit_http_works else '❌ Failed'}")
    print(f"Custom domain HTTP: {'✅ Working' if custom_http_works else '❌ Failed'}")
    
    # Determine problem
    if not custom_ip:
        print("\n❌ Problem detected: DNS resolution failed for custom domain")
        print("   This suggests your DNS records are not properly configured.")
    elif not custom_http_works and replit_http_works:
        print("\n❌ Problem detected: Custom domain HTTP request failed, but Replit domain works")
        print("   This suggests issues with domain verification or SSL configuration.")
    
    # Suggest fixes
    suggest_fixes(custom_domain)

if __name__ == "__main__":
    main()
