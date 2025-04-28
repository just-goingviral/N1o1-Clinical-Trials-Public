#!/usr/bin/env python3
"""
Fix Netlify blank screen issue (usually related to redirect loops)
"""
import os
import sys
import requests

def check_netlify_domain(domain):
    """Check if a Netlify domain is responding properly"""
    try:
        # Try with HTTPS first
        response = requests.get(f"https://{domain}", timeout=10)
        print(f"HTTPS response status: {response.status_code}")
        if response.status_code == 200:
            print("Domain is accessible via HTTPS")
            return True
    except Exception as e:
        print(f"HTTPS check failed: {e}")
    
    try:
        # Try with HTTP as fallback
        response = requests.get(f"http://{domain}", timeout=10)
        print(f"HTTP response status: {response.status_code}")
        if response.status_code == 200:
            print("Domain is accessible via HTTP")
            return True
    except Exception as e:
        print(f"HTTP check failed: {e}")
    
    return False

def fix_netlify_redirects(domain):
    """Create a proper _redirects file for Netlify"""
    redirects_content = """
# Netlify redirects file
# Fix for blank screens and redirect loops

# Force HTTP to prevent SSL redirect loops
http://*   /*    200
https://*  /*    200

# Fallback to index.html for SPA routing
/*    /index.html   200
"""
    
    # Write the redirects file
    with open("_redirects", "w") as f:
        f.write(redirects_content)
    
    print("Created Netlify _redirects file to fix blank screens and redirect loops")
    
    # If netlify.toml exists, update it too
    if os.path.exists("netlify.toml"):
        try:
            with open("netlify.toml", "r") as f:
                toml_content = f.read()
            
            # Check if [[redirects]] section exists
            if "[[redirects]]" not in toml_content:
                # Add redirects section
                toml_append = """
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  force = false
"""
                with open("netlify.toml", "a") as f:
                    f.write(toml_append)
                print("Updated netlify.toml with SPA redirect rule")
        except Exception as e:
            print(f"Error updating netlify.toml: {e}")

def check_html_meta():
    """Check index.html for meta tags that might cause redirect issues"""
    if not os.path.exists("index.html"):
        print("No index.html found to check")
        return
    
    try:
        with open("index.html", "r") as f:
            html_content = f.read().lower()
        
        # Check for problematic meta refreshes
        if '<meta http-equiv="refresh"' in html_content:
            print("WARNING: Found meta refresh tag in index.html which may cause redirect loops")
            
        # Check for canonical links
        if '<link rel="canonical"' in html_content and 'https:' in html_content:
            print("WARNING: Found canonical link with HTTPS which may cause redirect issues")
    
    except Exception as e:
        print(f"Error checking HTML: {e}")

def main():
    print("Netlify Blank Screen Fix Tool")
    print("----------------------------")
    
    # Get domain from command line or ask user
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = input("Enter your Netlify domain (e.g., your-site.netlify.app): ")
    
    # Check domain status
    print(f"\nChecking {domain}...")
    if check_netlify_domain(domain):
        print("\nYour domain is accessible but may have redirect issues.")
    else:
        print("\nYour domain is not accessible. There might be a deployment issue.")
    
    # Fix redirects configuration
    print("\nCreating proper redirect configuration...")
    fix_netlify_redirects(domain)
    
    # Check HTML for issues
    print("\nChecking for HTML issues...")
    check_html_meta()
    
    print("\nFixes applied. Please redeploy your site to Netlify.")
    print("Remember to check the following:")
    print("1. Ensure your browser cache is cleared")
    print("2. Check Netlify deploy logs for any errors")
    print("3. Verify DNS settings if using a custom domain")
    print("4. Disable 'Force HTTPS' in Netlify settings temporarily if needed")

if __name__ == "__main__":
    main()