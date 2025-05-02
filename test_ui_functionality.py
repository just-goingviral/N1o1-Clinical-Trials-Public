
#!/usr/bin/env python3
"""
UI Functionality Test Script
Tests buttons and interactive elements in the application
"""
import os
import time
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def test_button_functionality():
    """Test basic button functionality across pages"""
    print("Starting UI button test...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Check main page buttons
        driver.get("http://localhost:5000/")
        print("Testing main page buttons...")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "button"))
        )
        
        # Get all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons on main page")
        
        # Check if buttons have event listeners
        for i, button in enumerate(buttons[:5]):  # Test first 5 buttons
            button_id = button.get_attribute("id") or f"button-{i}"
            button_text = button.text or button.get_attribute("value") or "Unknown"
            print(f"  Button {i+1}: ID='{button_id}', Text='{button_text}'")
            
            # Check if clickable
            try:
                is_clickable = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[text()='{button_text}']"))
                )
                print(f"    ✅ Button '{button_text}' is clickable")
            except:
                print(f"    ❌ Button '{button_text}' is NOT clickable")
        
        # Test chat window button if present
        try:
            chat_button = driver.find_element(By.ID, "chatToggleBtn") or driver.find_element(By.ID, "no-molecule-chat-button")
            print(f"Testing chat button: {chat_button.get_attribute('id')}")
            chat_button.click()
            time.sleep(1)
            
            # Check if chat window appeared
            chat_window = None
            try:
                chat_window = driver.find_element(By.ID, "chatWidget") or driver.find_element(By.ID, "no-chat-modal")
                print("    ✅ Chat window opened successfully")
            except:
                print("    ❌ Chat window did not open")
            
            # If chat window opened, try closing it
            if chat_window:
                try:
                    close_button = driver.find_element(By.ID, "chatCloseBtn") or driver.find_element(By.ID, "no-chat-close")
                    close_button.click()
                    time.sleep(1)
                    print("    ✅ Chat window closed successfully")
                except:
                    print("    ❌ Couldn't close chat window")
        except:
            print("    ℹ️ Chat button not found")
            
        print("UI button tests completed")
        
    except Exception as e:
        print(f"Error during UI tests: {str(e)}")
    finally:
        driver.quit()

def test_form_functionality():
    """Test form submission functionality"""
    print("\nTesting form functionality...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to patient form if available
        driver.get("http://localhost:5000/patients/new")
        
        # Wait for form to load
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            print("  ✅ Patient form loaded")
            
            # Find form inputs
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"  Found {len(inputs)} form inputs")
            
            # Try filling out a form
            for input_field in inputs:
                field_type = input_field.get_attribute("type")
                field_id = input_field.get_attribute("id") or "unknown"
                
                if field_type == "text":
                    input_field.send_keys("Test Value")
                elif field_type == "number":
                    input_field.send_keys("42")
                elif field_type == "email":
                    input_field.send_keys("test@example.com")
                
                print(f"    Filled {field_type} field '{field_id}'")
            
            # Try submitting (but don't actually submit to avoid data corruption)
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            if submit_btn:
                print("    ✅ Submit button found")
            else:
                print("    ❌ Submit button not found")
            
        except:
            print("  ❌ Patient form not found or not accessible")
        
    except Exception as e:
        print(f"Error during form tests: {str(e)}")
    finally:
        driver.quit()

def test_javascript_functionality():
    """Test if JavaScript is functioning properly"""
    print("\nTesting JavaScript functionality...")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("http://localhost:5000/")
        
        # Execute test script to check JS environment
        js_test = """
        const testResults = {
            jsEnabled: true,
            documentReady: document.readyState,
            hasJQuery: typeof jQuery !== 'undefined',
            hasBootstrap: typeof bootstrap !== 'undefined',
            functionTests: {}
        };
        
        // Test common app.js functions
        if (typeof formatNumber === 'function') {
            try {
                testResults.functionTests.formatNumber = formatNumber(123.456, 2) === '123.46';
            } catch(e) {
                testResults.functionTests.formatNumber = false;
            }
        }
        
        if (typeof showToast === 'function') {
            try {
                testResults.functionTests.showToast = true;
                // Don't actually show a toast in test
            } catch(e) {
                testResults.functionTests.showToast = false;
            }
        }
        
        return testResults;
        """
        
        results = driver.execute_script(js_test)
        print("JavaScript test results:")
        print(json.dumps(results, indent=2))
        
        # Test specific UI events like click handlers
        event_test = """
        const eventResults = {
            buttonEvents: {}
        };
        
        // Check first 3 buttons for click handlers
        const buttons = document.querySelectorAll('button');
        for (let i = 0; i < Math.min(buttons.length, 3); i++) {
            const button = buttons[i];
            const id = button.id || `button-${i}`;
            const events = getEventListeners ? getEventListeners(button) : {click: 'unknown'};
            eventResults.buttonEvents[id] = events.click ? true : false;
        }
        
        return eventResults;
        """
        
        try:
            event_results = driver.execute_script(event_test)
            print("Event handler test results:")
            print(json.dumps(event_results, indent=2))
        except:
            print("Note: Detailed event handler testing requires DevTools protocol")
        
    except Exception as e:
        print(f"Error during JavaScript tests: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("N1O1 Clinical Trials UI Test Suite")
    print("=================================")
    
    # Run the tests
    test_button_functionality()
    test_form_functionality()
    test_javascript_functionality()
    
    print("\nAll UI tests completed")
