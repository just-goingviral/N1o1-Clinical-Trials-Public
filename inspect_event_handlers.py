#!/usr/bin/env python3
"""
Event Handler Inspector
Analyzes HTML files to check for proper event handling on interactive elements
"""

import os
import re
import sys
import json
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EventHandlerInspector:
    def __init__(self):
        self.interactive_elements = [
            'button', 'a', 'input', 'select', 'textarea', 
            '[role="button"]', '.btn', 'form'
        ]

        self.event_attributes = [
            'onclick', 'onsubmit', 'onchange', 'oninput', 'onkeyup', 'onkeydown',
            'onblur', 'onfocus', 'onmouseover', 'onmouseout', 'data-action',
            'data-bs-toggle', 'data-toggle'
        ]

        self.missing_attributes = [
            'id', 'name', 'aria-label', 'type'
        ]

    def inspect_html_file(self, file_path):
        """Inspect a single HTML file for event handler issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            soup = BeautifulSoup(content, 'html.parser')
            issues = []

            # Check each interactive element
            for selector in self.interactive_elements:
                elements = soup.select(selector)

                for element in elements:
                    element_id = element.get('id', '')
                    element_class = element.get('class', [])
                    if isinstance(element_class, list):
                        element_class = ' '.join(element_class)

                    element_desc = f"{element.name}"
                    if element_id:
                        element_desc += f"#{element_id}"
                    elif element_class:
                        element_desc += f".{element_class}"

                    # Check for missing event handlers
                    has_event_handler = False
                    for attr in self.event_attributes:
                        if element.has_attr(attr):
                            has_event_handler = True
                            break

                    # Check for form elements with submit buttons
                    if element.name == 'form':
                        submit_buttons = element.select('button[type="submit"], input[type="submit"]')
                        if not submit_buttons and not has_event_handler:
                            issues.append(f"{element_desc} has no submit button or event handler")

                    # Check for buttons without handlers (excluding submit/reset buttons)
                    elif element.name == 'button':
                        button_type = element.get('type', '')
                        if not has_event_handler and button_type not in ['submit', 'reset']:
                            if not element.find_parent('form'):  # Not in a form
                                issues.append(f"{element_desc} has no event handler")

                    # Check for links without href
                    elif element.name == 'a' and not element.has_attr('href') and not has_event_handler:
                        issues.append(f"{element_desc} has no href or event handler")

                    # Check for missing accessibility attributes
                    missing_attrs = []
                    for attr in self.missing_attributes:
                        if not element.has_attr(attr):
                            missing_attrs.append(attr)

                    if missing_attrs and element.name != 'form':  # Skip form for these checks
                        issues.append(f"{element_desc} is missing attributes: {', '.join(missing_attrs)}")

            return file_path, issues

        except Exception as e:
            return file_path, [f"Error inspecting file: {str(e)}"]

    def scan_template_directory(self, directory='templates'):
        """Scan all HTML files in the templates directory"""
        html_files = []

        # Find all HTML files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))

        results = []
        for html_file in html_files:
            file_path, issues = self.inspect_html_file(html_file)
            results.append((file_path, issues))

        return results

    def generate_fix_suggestions(self, results):
        """Generate suggestions to fix the issues"""
        suggestions = []

        for file_path, issues in results:
            if issues:
                file_suggestion = {
                    "file": file_path,
                    "issues": issues,
                    "suggestions": []
                }

                for issue in issues:
                    if "has no event handler" in issue:
                        element_type = issue.split(' ')[0]
                        if element_type == "button":
                            file_suggestion["suggestions"].append(
                                "Add a click handler or data-action attribute to the button"
                            )
                        elif element_type == "a":
                            file_suggestion["suggestions"].append(
                                "Add an href attribute or click handler to the link"
                            )
                        elif element_type == "form":
                            file_suggestion["suggestions"].append(
                                "Add a submit button or onsubmit handler to the form"
                            )
                    elif "missing attributes" in issue:
                        file_suggestion["suggestions"].append(
                            "Add appropriate accessibility attributes for better usability"
                        )

                suggestions.append(file_suggestion)

        return suggestions

def main():
    logger.info("Starting event handler inspection...")

    inspector = EventHandlerInspector()

    # Scan templates directory
    results = inspector.scan_template_directory()

    # Display results
    files_with_issues = 0
    total_issues = 0

    for file_path, issues in results:
        if issues:
            files_with_issues += 1
            total_issues += len(issues)

            logger.info(f"\nFile: {file_path}")
            for issue in issues:
                logger.info(f"  - {issue}")
        else:
            logger.info(f"✅ {file_path} - No issues found")

    # Generate fix suggestions
    if files_with_issues > 0:
        logger.info("\n--- Fix Suggestions ---")
        suggestions = inspector.generate_fix_suggestions(results)

        for suggestion in suggestions:
            if suggestion["suggestions"]:
                logger.info(f"\nFor {suggestion['file']}:")
                for fix in suggestion["suggestions"]:
                    logger.info(f"  - {fix}")

    # Summary
    logger.info("\n--- Summary ---")
    logger.info(f"Total files checked: {len(results)}")
    logger.info(f"Files with issues: {files_with_issues}")
    logger.info(f"Total issues found: {total_issues}")

    if total_issues == 0:
        logger.info("All event handlers look good!")

    return total_issues == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)