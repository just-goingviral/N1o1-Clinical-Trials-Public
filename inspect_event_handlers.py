
#!/usr/bin/env python3
"""
Event Handler Inspector
Analyzes the event handlers attached to buttons and other UI elements
"""
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Set up Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def inspect_event_handlers():
    """Inspect event handlers on UI elements"""
    print("Inspecting event handlers on UI elements...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to the main page
        driver.get("http://localhost:5000/")
        time.sleep(2)
        
        # Run JavaScript to extract event handlers
        js_script = """
        // Initialize results object
        const results = {
            buttons: [],
            inputs: [],
            links: [],
            summaryStats: {}
        };
        
        // Check for event listeners on buttons
        document.querySelectorAll('button').forEach((button, index) => {
            const id = button.id || 'btn-' + index;
            const text = button.textContent.trim();
            const classes = Array.from(button.classList);
            
            // Check if the button has onclick attribute
            const hasOnclick = button.hasAttribute('onclick');
            
            // Check if the button has any Bootstrap event handlers
            const hasBootstrapHandlers = button.hasAttribute('data-bs-toggle') || 
                                         button.hasAttribute('data-bs-target') ||
                                         button.hasAttribute('data-toggle') ||
                                         button.hasAttribute('data-target');
            
            // Store button info
            results.buttons.push({
                id,
                text: text || '[Empty Button]',
                classes,
                hasOnclick,
                hasBootstrapHandlers,
                attributes: Object.fromEntries(
                    Array.from(button.attributes)
                        .map(attr => [attr.name, attr.value])
                )
            });
        });
        
        // Check inputs for event handlers
        document.querySelectorAll('input, select, textarea').forEach((input, index) => {
            const id = input.id || 'input-' + index;
            const type = input.type || input.tagName.toLowerCase();
            
            // Check for inline event handlers
            const hasOnchange = input.hasAttribute('onchange');
            const hasOninput = input.hasAttribute('oninput');
            const hasOnfocus = input.hasAttribute('onfocus');
            const hasOnblur = input.hasAttribute('onblur');
            
            results.inputs.push({
                id,
                type,
                hasOnchange,
                hasOninput,
                hasOnfocus,
                hasOnblur,
                attributes: Object.fromEntries(
                    Array.from(input.attributes)
                        .map(attr => [attr.name, attr.value])
                )
            });
        });
        
        // Check links for event handlers
        document.querySelectorAll('a').forEach((link, index) => {
            const id = link.id || 'link-' + index;
            const text = link.textContent.trim();
            const href = link.getAttribute('href');
            
            // Check if it's an AJAX link or has a click handler
            const isAjaxLink = href === '#' || href === 'javascript:void(0)' || !href;
            const hasOnclick = link.hasAttribute('onclick');
            
            results.links.push({
                id,
                text: text || '[Empty Link]',
                href,
                isAjaxLink,
                hasOnclick,
                attributes: Object.fromEntries(
                    Array.from(link.attributes)
                        .map(attr => [attr.name, attr.value])
                )
            });
        });
        
        // Calculate summary statistics
        results.summaryStats = {
            totalButtons: results.buttons.length,
            buttonsWithHandlers: results.buttons.filter(b => b.hasOnclick || b.hasBootstrapHandlers).length,
            totalInputs: results.inputs.length,
            inputsWithHandlers: results.inputs.filter(i => i.hasOnchange || i.hasOninput || i.hasOnfocus || i.hasOnblur).length,
            totalLinks: results.links.length,
            linksWithHandlers: results.links.filter(l => l.hasOnclick || l.isAjaxLink).length
        };
        
        return results;
        """
        
        results = driver.execute_script(js_script)
        
        # Display the results
        print("\nEvent Handler Summary:")
        print(f"Found {results['summaryStats']['totalButtons']} buttons, {results['summaryStats']['buttonsWithHandlers']} with handlers")
        print(f"Found {results['summaryStats']['totalInputs']} inputs, {results['summaryStats']['inputsWithHandlers']} with handlers")
        print(f"Found {results['summaryStats']['totalLinks']} links, {results['summaryStats']['linksWithHandlers']} with handlers")
        
        # Report on buttons with no handlers
        problematic_buttons = [b for b in results['buttons'] if not (b['hasOnclick'] or b['hasBootstrapHandlers'])]
        if problematic_buttons:
            print("\nButtons with no event handlers:")
            for btn in problematic_buttons[:5]:  # Show first 5 only
                print(f"  • '{btn['text']}' (ID: {btn['id']}, Classes: {', '.join(btn['classes'])})")
            
            if len(problematic_buttons) > 5:
                print(f"  ... and {len(problematic_buttons) - 5} more")
        
        # Report on AJAX links with no handlers
        problematic_links = [l for l in results['links'] if l['isAjaxLink'] and not l['hasOnclick']]
        if problematic_links:
            print("\nAJAX-style links with no click handlers:")
            for link in problematic_links[:5]:  # Show first 5 only
                print(f"  • '{link['text']}' (ID: {link['id']}, href: {link['href']})")
            
            if len(problematic_links) > 5:
                print(f"  ... and {len(problematic_links) - 5} more")
        
        # Save full results to a file
        with open('event_handler_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\nDetailed report saved to event_handler_report.json")
        
    except Exception as e:
        print(f"Error inspecting event handlers: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("N1O1 Clinical Trials Event Handler Inspector")
    print("=========================================")
    inspect_event_handlers()
    print("\nEvent handler inspection completed")
