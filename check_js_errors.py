
#!/usr/bin/env python3
"""
JavaScript Console Error Detector
Checks for JavaScript errors in the console when interacting with the application
"""
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--log-level=3')

def check_js_errors():
    """Check for JavaScript errors in the console"""
    print("Checking for JavaScript errors...")
    driver = webdriver.Chrome(options=options)
    
    # Store the URLs to test
    urls_to_test = [
        "http://localhost:5000/",                # Main page
        "http://localhost:5000/patients",        # Patients page
        "http://localhost:5000/simulations/new"  # New simulation page
    ]
    
    try:
        for url in urls_to_test:
            print(f"\nChecking JavaScript errors on {url}")
            driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get console logs
            logs = driver.get_log('browser')
            
            if logs:
                print(f"Found {len(logs)} log entries:")
                error_count = 0
                for log in logs:
                    if log['level'] == 'SEVERE':
                        error_count += 1
                        print(f"  ❌ ERROR: {log['message']}")
                    elif 'error' in log['message'].lower():
                        error_count += 1
                        print(f"  ❌ ERROR: {log['message']}")
                    else:
                        print(f"  ℹ️ {log['level']}: {log['message']}")
                
                if error_count > 0:
                    print(f"  Found {error_count} JavaScript errors on {url}")
                else:
                    print(f"  ✅ No JavaScript errors found on {url}")
            else:
                print(f"  ✅ No JavaScript logs found on {url}")
            
            # Try clicking some buttons to check for dynamic errors
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for i, button in enumerate(buttons[:3]):  # Test first 3 buttons only
                    try:
                        print(f"  Clicking button: {button.text or button.get_attribute('id') or f'Button #{i}'}")
                        button.click()
                        time.sleep(1)
                        
                        # Check for new errors
                        new_logs = driver.get_log('browser')
                        new_errors = [log for log in new_logs if log['level'] == 'SEVERE' or 'error' in log['message'].lower()]
                        
                        if new_errors:
                            print(f"  ❌ Found {len(new_errors)} errors after clicking button")
                            for error in new_errors:
                                print(f"    {error['message']}")
                        else:
                            print("  ✅ No errors after button click")
                    except Exception as click_error:
                        print(f"  ❌ Error clicking button: {str(click_error)}")
            except Exception as e:
                print(f"  ℹ️ Could not test buttons: {str(e)}")
    
    except Exception as e:
        print(f"Error checking for JavaScript errors: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("N1O1 Clinical Trials JavaScript Error Detector")
    print("============================================")
    check_js_errors()
    print("\nJavaScript error check completed")
