
#!/usr/bin/env python3
"""
Advanced JavaScript error checker
Performs static analysis on JavaScript files to detect common issues
"""

import os
import re
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class JSErrorChecker:
    def __init__(self):
        self.error_patterns = [
            (r'console\.error\(', 'Console error calls'),
            (r'throw\s+new\s+Error', 'Throw statements'),
            (r'catch\s*\(', 'Exception handling'),
            (r'undefined|null', 'Potential null/undefined usage'),
            (r'\/\/\s*TODO|\/\/\s*FIXME', 'TODO/FIXME comments'),
            (r'alert\(', 'Alert usage'),
        ]
        
        self.syntax_patterns = [
            (r'[^\w"\']\.{3}[^\w"\']', 'Potential syntax error with ellipsis'),
            (r'[^;{}\n]\n\s*\}', 'Missing semicolon before block end'),
            (r'\)\s*\{', 'Function definition issue'),
            (r'\w+\s*\(', 'Function calls'),
        ]
        
        self.event_handler_patterns = [
            (r'addEventListener\(', 'Event listeners'),
            (r'on\w+\s*=', 'Inline event handlers'),
            (r'onClick|onChange|onSubmit', 'React event handlers'),
            (r'\$\([^)]+\)\.on\(', 'jQuery event handlers')
        ]

    def check_script(self, file_path):
        if not os.path.exists(file_path):
            return file_path, [f"File not found: {file_path}"]
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues = []
            
            # Check for error handling
            for pattern, label in self.error_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    issues.append(f"Found {len(matches)} {label}")
            
            # Check for syntax issues
            for pattern, label in self.syntax_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    issues.append(f"Found {len(matches)} potential {label}")
            
            # Check for event handlers
            event_handlers = []
            for pattern, label in self.event_handler_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    event_handlers.append(f"{len(matches)} {label}")
            
            if event_handlers:
                issues.append(f"Event handlers: {', '.join(event_handlers)}")
            
            # Check for unclosed parentheses and braces
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens != close_parens:
                issues.append(f"Mismatched parentheses: {open_parens} opening, {close_parens} closing")
                
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                issues.append(f"Mismatched braces: {open_braces} opening, {close_braces} closing")
            
            return file_path, issues
            
        except Exception as e:
            return file_path, [f"Error checking file: {str(e)}"]

    def scan_js_files(self, directory='static/js'):
        """Scan all JavaScript files in the project"""
        js_files = []
        
        # Find all JS files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
                    
        # Check each file
        results = []
        for js_file in js_files:
            file_path, issues = self.check_script(js_file)
            results.append((file_path, issues))
            
        return results
    
    def scan_html_for_js(self, directory='templates'):
        """Scan HTML files for inline JavaScript"""
        html_files = []
        
        # Find all HTML files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
        
        # Check each file for script tags
        results = []
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for script tags
                script_tags = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
                
                if script_tags:
                    issues = [f"Found {len(script_tags)} script blocks"]
                    
                    # Check content of script tags
                    for script in script_tags:
                        if len(script.strip()) > 0:
                            # Check for error handling in inline scripts
                            for pattern, label in self.error_patterns:
                                matches = re.findall(pattern, script)
                                if matches:
                                    issues.append(f"Inline script contains {len(matches)} {label}")
                            
                            # Check for event handlers in inline scripts
                            for pattern, label in self.event_handler_patterns:
                                matches = re.findall(pattern, script)
                                if matches:
                                    issues.append(f"Inline script contains {len(matches)} {label}")
                    
                    results.append((html_file, issues))
            except Exception as e:
                results.append((html_file, [f"Error scanning file: {str(e)}"]))
        
        return results

def main():
    logger.info("Starting JavaScript error check...")
    
    checker = JSErrorChecker()
    
    # Check all JS files
    logger.info("\n--- Checking JavaScript Files ---")
    js_results = checker.scan_js_files()
    
    for file_path, issues in js_results:
        if issues:
            logger.info(f"\nFile: {file_path}")
            for issue in issues:
                logger.info(f"  - {issue}")
        else:
            logger.info(f"✅ {file_path} - No issues found")
    
    # Check HTML files for inline scripts
    logger.info("\n--- Checking HTML Files for Inline Scripts ---")
    html_results = checker.scan_html_for_js()
    
    for file_path, issues in html_results:
        if issues:
            logger.info(f"\nFile: {file_path}")
            for issue in issues:
                logger.info(f"  - {issue}")
    
    # Summary
    total_js_files = len(js_results)
    js_files_with_issues = sum(1 for _, issues in js_results if issues)
    
    total_html_files = len(html_results)
    html_files_with_issues = sum(1 for _, issues in html_results if issues)
    
    logger.info("\n--- Summary ---")
    logger.info(f"JavaScript files checked: {total_js_files}")
    logger.info(f"JavaScript files with issues: {js_files_with_issues}")
    logger.info(f"HTML files with inline scripts checked: {total_html_files}")
    logger.info(f"HTML files with script issues: {html_files_with_issues}")
    
    return js_files_with_issues == 0 and html_files_with_issues == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
