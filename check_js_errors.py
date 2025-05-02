
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_script(file_path):
    """Check a JavaScript file for common errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # List of potential issues to check
        issues = []
        
        # Check for console.log statements (not necessarily errors but should be removed in production)
        console_logs = len(re.findall(r'console\.log\(', content))
        if console_logs > 0:
            issues.append(f"Found {console_logs} console.log statements")
            
        # Check for missing semicolons after statements
        missing_semicolons = len(re.findall(r'(var|let|const|return|throw|new|delete|typeof|void|function\s+\w+)\s+[^;{}]*$', content, re.MULTILINE))
        if missing_semicolons > 0:
            issues.append(f"Potentially missing {missing_semicolons} semicolons")
        
        # Check for undefined/null references
        null_checks = len(re.findall(r'if\s*\(\s*\w+\s*\)\s*{', content))
        if null_checks > 5:  # Only flag if there are several without explicit comparison
            issues.append(f"Found {null_checks} potential implicit null/undefined checks")
            
        # Check for event listeners without error handling
        event_listeners = len(re.findall(r'addEventListener\(', content))
        try_catch_blocks = len(re.findall(r'try\s*{', content))
        if event_listeners > try_catch_blocks:
            issues.append(f"Found {event_listeners} event listeners but only {try_catch_blocks} try-catch blocks")
            
        # Check for potential memory leaks (event listeners without removal)
        if 'addEventListener' in content and 'removeEventListener' not in content:
            issues.append("Event listeners added but never removed (potential memory leak)")
            
        # Check for hardcoded URLs
        hardcoded_urls = len(re.findall(r'https?://[^\s\'"]+', content))
        if hardcoded_urls > 0:
            issues.append(f"Found {hardcoded_urls} hardcoded URLs")
        
        return file_path, issues
        
    except Exception as e:
        logger.error(f"Error checking {file_path}: {str(e)}")
        return file_path, [f"Error analyzing file: {str(e)}"]

def scan_js_files():
    """Scan all JavaScript files in the project"""
    js_files = []
    
    # Find all JS files
    for root, _, files in os.walk('static/js'):
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
                
    # Check each file
    results = []
    for js_file in js_files:
        file_path, issues = check_script(js_file)
        results.append((file_path, issues))
        
    return results

def fix_common_button_issues():
    """Check and suggest fixes for common button functionality issues"""
    issues_found = False
    
    # Check if button-fix.js is properly included in base template
    base_template_path = 'templates/base.html'
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'button-fix.js' not in content:
            logger.warning("❌ button-fix.js is not included in base.html")
            issues_found = True
            
    # Check for incomplete button-fix.js implementation
    button_fix_path = 'static/js/button-fix.js'
    if os.path.exists(button_fix_path):
        with open(button_fix_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'fixStretchedLinks' in content and 'fixStretchedLinks()' not in content:
            logger.warning("❌ fixStretchedLinks function exists but is not called")
            issues_found = True
    
    return issues_found

if __name__ == "__main__":
    logger.info("Starting JavaScript error check...")
    
    # Scan all JS files
    results = scan_js_files()
    
    # Report results
    print("\n--- JavaScript File Analysis ---")
    total_issues = 0
    
    for file_path, issues in results:
        if issues:
            logger.info(f"\n{file_path}:")
            for issue in issues:
                logger.warning(f"  ⚠️ {issue}")
                total_issues += 1
        else:
            logger.info(f"✅ {file_path}: No issues found")
    
    # Check for button-specific issues
    button_issues = fix_common_button_issues()
    
    # Summary
    logger.info("\n--- Summary ---")
    logger.info(f"Total files checked: {len(results)}")
    logger.info(f"Total issues found: {total_issues}")
    
    if total_issues == 0 and not button_issues:
        logger.info("✅ No JavaScript issues detected!")
    else:
        logger.warning("⚠️ Some JavaScript issues were found. See details above.")
