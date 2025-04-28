#!/usr/bin/env python3
"""
Diagnose redirect loops and blank screen issues for web applications
"""
import os
import sys
import time
import json
import subprocess
import requests

def check_domain(url, max_redirects=10):
    """Check a domain for redirect issues"""
    print(f"Checking URL: {url}")
    print("-" * 50)
    
    redirects = []
    current_url = url
    
    try:
        for i in range(max_redirects):
            # Don't follow redirects automatically
            response = requests.get(
                current_url, 
                allow_redirects=False, 
                timeout=10, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            
            status = response.status_code
            redirects.append({
                'url': current_url,
                'status': status,
                'location': response.headers.get('Location', None),
                'server': response.headers.get('Server', None),
                'content_type': response.headers.get('Content-Type', None),
                'content_length': len(response.content),
            })
            
            print(f"Request {i+1}: {current_url}")
            print(f"Status: {status}")
            
            # Check for redirect status codes
            if 300 <= status < 400 and 'Location' in response.headers:
                location = response.headers['Location']
                print(f"Redirect to: {location}")
                current_url = location if location.startswith('http') else f"{'://'.join(current_url.split('://')[:1])}{location}"
            else:
                # Not a redirect, show headers and break
                print("Headers:")
                for key, value in response.headers.items():
                    print(f"  {key}: {value}")
                
                # Check if content is very short (possibly blank page)
                if len(response.content) < 100:
                    print("\nWARNING: Very short content detected, possibly a blank page")
                    print(f"Content ({len(response.content)} bytes):")
                    print(response.content.decode('utf-8', errors='ignore'))
                else:
                    print(f"\nContent length: {len(response.content)} bytes")
                    # Check for HTML title
                    if response.headers.get('Content-Type', '').startswith('text/html'):
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(response.content, 'html.parser')
                            title = soup.title.string if soup.title else "No title found"
                            print(f"Page title: {title}")
                        except ImportError:
                            print("BeautifulSoup not installed, skipping HTML parsing")
                
                break
        else:
            print(f"\nERROR: Too many redirects (>{max_redirects})")
            
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: {str(e)}")
        redirects.append({
            'url': current_url,
            'error': str(e)
        })
    
    return redirects

def check_domain_with_curl(url):
    """Use curl to check a domain with full headers"""
    print(f"\nDetailed curl check for {url}")
    print("-" * 50)
    
    try:
        # Use curl with verbose output and headers
        curl_cmd = [
            'curl', '-v', '-L', 
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            '--max-redirs', '15',
            url
        ]
        
        # Capture both stdout and stderr
        process = subprocess.Popen(
            curl_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate()
        
        # Stderr contains the headers and verbose info
        print(stderr)
        
        # Only print first 500 chars of stdout if it's large
        content_preview = stdout[:500] + "..." if len(stdout) > 500 else stdout
        print(f"\nContent preview:\n{content_preview}")
        
        return True
    except Exception as e:
        print(f"Curl check failed: {str(e)}")
        return False

def check_browser_simulation(url):
    """Simulate browser behavior for redirect checking"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        print(f"\nSimulating browser visit to {url}")
        print("-" * 50)
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        try:
            # Navigate to URL
            driver.get(url)
            
            # Get final URL after any redirects
            final_url = driver.current_url
            print(f"Final URL: {final_url}")
            
            # Get page title
            title = driver.title
            print(f"Page title: {title}")
            
            # Get page source length
            source_length = len(driver.page_source)
            print(f"Page source length: {source_length} bytes")
            
            # Check if page is blank (very short source)
            if source_length < 100:
                print("WARNING: Very short page source, possibly a blank page")
                print(f"Page source:\n{driver.page_source}")
            
            # Capture any console errors
            logs = driver.get_log('browser')
            if logs:
                print("\nBrowser console errors:")
                for log in logs:
                    print(f"  {log}")
            
            return {
                'url': url,
                'final_url': final_url,
                'title': title,
                'source_length': source_length
            }
            
        finally:
            driver.quit()
            
    except ImportError:
        print("Selenium not installed, skipping browser simulation")
        return None
    except Exception as e:
        print(f"Browser simulation failed: {str(e)}")
        return None

def main():
    """Main function"""
    print("Redirect Loop and Blank Screen Diagnostic Tool")
    print("=" * 50)
    
    # Get URL from command line or prompt user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to check (e.g., https://neral-kataifi-590c5c.netlify.app): ")
    
    # Default to https if no protocol specified
    if not url.startswith('http'):
        url = 'https://' + url
    
    # Check both HTTP and HTTPS versions
    http_url = 'http://' + url.split('://', 1)[1]
    https_url = 'https://' + url.split('://', 1)[1]
    
    results = {}
    
    # Check HTTPS version
    print("\nChecking HTTPS version...")
    results['https'] = check_domain(https_url)
    
    # Check HTTP version
    print("\nChecking HTTP version...")
    results['http'] = check_domain(http_url)
    
    # Use curl for more detailed checks
    check_domain_with_curl(url)
    
    # Try browser simulation if available
    browser_result = check_browser_simulation(url)
    if browser_result:
        results['browser'] = browser_result
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    result_file = f"redirect_diagnosis_{timestamp}.json"
    
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDiagnosis complete. Results saved to {result_file}")
    
    # Provide recommendations
    print("\nRecommendations based on diagnosis:")
    
    # Check for obvious redirect loops
    redirect_loop = False
    for check in ['http', 'https']:
        urls = [r.get('url') for r in results.get(check, []) if 'url' in r]
        if len(urls) > len(set(urls)):
            redirect_loop = True
            break
    
    if redirect_loop:
        print("\n1. Redirect loop detected. Recommended fixes:")
        print("   - Create or update Netlify _redirects file (see fix_netlify_domain.sh)")
        print("   - Temporarily disable 'Force HTTPS' in Netlify settings")
        print("   - Check for meta refresh tags in HTML")
    else:
        print("\n1. No obvious redirect loop detected. Issues may be related to:")
        print("   - Content blocking or CORS issues")
        print("   - JavaScript errors preventing page rendering")
        print("   - DNS or deployment problems")
    
    # Check for HTTP vs HTTPS differences
    http_success = any(300 > r.get('status', 500) < 400 for r in results.get('http', []) if 'status' in r)
    https_success = any(300 > r.get('status', 500) < 400 for r in results.get('https', []) if 'status' in r)
    
    if http_success and not https_success:
        print("\n2. HTTP works but HTTPS fails. Recommended fixes:")
        print("   - Check SSL certificate configuration")
        print("   - Verify HTTPS settings in Netlify")
    elif https_success and not http_success:
        print("\n2. HTTPS works but HTTP fails. This likely indicates forced HTTPS redirects.")
        print("   - Try accessing the site directly with HTTPS")
    
    print("\n3. General troubleshooting steps:")
    print("   - Clear browser cache and cookies")
    print("   - Try accessing in incognito/private browsing mode")
    print("   - Check browser console for JavaScript errors")
    print("   - Review Netlify deploy logs")

if __name__ == "__main__":
    main()