
import os
import re
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventHandlerInspector:
    def __init__(self):
        self.handlers = {}
        self.issues = []
        
    def scan_js_files(self):
        """Scan all JavaScript files for event handlers"""
        js_files = []
        
        # Find all JS files
        for root, _, files in os.walk('static/js'):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
        
        # Scan each file
        for js_file in js_files:
            self.scan_file(js_file)
            
    def scan_file(self, file_path):
        """Scan a single file for event handlers"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for addEventListener calls
            add_listener_pattern = r'(\w+)\.addEventListener\s*\(\s*[\'"](\w+)[\'"]\s*,\s*(\w+)'
            matches = re.findall(add_listener_pattern, content)
            
            for element, event_type, handler in matches:
                key = f"{element}:{event_type}"
                if key not in self.handlers:
                    self.handlers[key] = []
                self.handlers[key].append({
                    'file': file_path,
                    'handler': handler,
                    'code': self.extract_handler_code(content, handler)
                })
                
            # Look for onclick and other inline event assignments
            inline_pattern = r'(\w+)\.on(\w+)\s*=\s*(\w+|\(\s*(?:[^)(]*|\((?:[^)(]*|\([^)(]*\))*\))*\)\s*=>\s*{)'
            inline_matches = re.findall(inline_pattern, content)
            
            for element, event_type, handler in inline_matches:
                key = f"{element}:on{event_type}"
                if key not in self.handlers:
                    self.handlers[key] = []
                    
                # Handle both named functions and arrow functions
                if handler.startswith('(') and '=>' in handler:
                    handler_name = 'anonymous_function'
                    handler_code = handler
                else:
                    handler_name = handler
                    handler_code = self.extract_handler_code(content, handler)
                    
                self.handlers[key].append({
                    'file': file_path,
                    'handler': handler_name,
                    'code': handler_code
                })
                
            # Check for common issues
            self.check_event_issues(file_path, content)
            
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {str(e)}")
    
    def extract_handler_code(self, content, handler_name):
        """Extract the code for a named handler function"""
        # Look for function declaration
        func_pattern = rf'function\s+{handler_name}\s*\([^)]*\)\s*{{([^}}]*)}}'
        matches = re.search(func_pattern, content)
        
        if matches:
            return f"function {handler_name}() {{ {matches.group(1)} }}"
        
        # Look for const/let/var assignment with function
        assignment_pattern = rf'(?:const|let|var)\s+{handler_name}\s*=\s*function\s*\([^)]*\)\s*{{([^}}]*)}}'
        matches = re.search(assignment_pattern, content)
        
        if matches:
            return f"{handler_name} = function() {{ {matches.group(1)} }}"
            
        # Look for arrow function
        arrow_pattern = rf'(?:const|let|var)\s+{handler_name}\s*=\s*\([^)]*\)\s*=>\s*{{([^}}]*)}}'
        matches = re.search(arrow_pattern, content)
        
        if matches:
            return f"{handler_name} = () => {{ {matches.group(1)} }}"
            
        return "// Handler code not found"
    
    def check_event_issues(self, file_path, content):
        """Check for common event handler issues"""
        # Check for event.preventDefault without try/catch
        if 'preventDefault' in content:
            prevent_default_count = content.count('preventDefault')
            try_catch_count = content.count('try {')
            
            if prevent_default_count > try_catch_count:
                self.issues.append({
                    'file': file_path,
                    'issue': 'event.preventDefault() called without try/catch',
                    'severity': 'Medium'
                })
                
        # Check for stopPropagation without try/catch
        if 'stopPropagation' in content:
            stop_prop_count = content.count('stopPropagation')
            try_catch_count = content.count('try {')
            
            if stop_prop_count > try_catch_count:
                self.issues.append({
                    'file': file_path,
                    'issue': 'event.stopPropagation() called without try/catch',
                    'severity': 'Medium'
                })
                
        # Check for double event binding
        if content.count('addEventListener') > content.count('removeEventListener'):
            self.issues.append({
                'file': file_path,
                'issue': 'More addEventListener calls than removeEventListener calls',
                'severity': 'Low'
            })
            
    def check_button_handlers(self):
        """Check specifically for button-related event handlers"""
        # Look for button click handlers in HTML files
        button_handlers = {}
        
        for root, _, files in os.walk('templates'):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check for inline button handlers
                        button_pattern = r'<button[^>]*\s+onclick\s*=\s*[\'"]([^\'"]*)[\'"]'
                        matches = re.findall(button_pattern, content)
                        
                        for handler in matches:
                            if handler not in button_handlers:
                                button_handlers[handler] = []
                            button_handlers[handler].append(file_path)
                            
                        # Check for button ids (for DOM event listeners)
                        id_pattern = r'<button[^>]*\s+id\s*=\s*[\'"]([^\'"]*)[\'"]'
                        id_matches = re.findall(id_pattern, content)
                        
                        if id_matches:
                            # Check if we have handlers for these buttons
                            for button_id in id_matches:
                                found = False
                                for key in self.handlers:
                                    if button_id in key:
                                        found = True
                                        break
                                        
                                if not found:
                                    self.issues.append({
                                        'file': file_path,
                                        'issue': f'Button with id "{button_id}" has no registered event handler',
                                        'severity': 'High'
                                    })
                                    
                    except Exception as e:
                        logger.error(f"Error checking {file_path}: {str(e)}")
        
        return button_handlers
    
    def generate_report(self):
        """Generate a report of all findings"""
        button_handlers = self.check_button_handlers()
        
        report = {
            'event_handlers': self.handlers,
            'button_handlers': button_handlers,
            'issues': self.issues
        }
        
        return report

def main():
    logger.info("Starting event handler inspection...")
    
    inspector = EventHandlerInspector()
    inspector.scan_js_files()
    
    report = inspector.generate_report()
    
    # Display summary
    logger.info("\n--- Event Handler Summary ---")
    logger.info(f"Found {len(report['event_handlers'])} unique event handlers")
    logger.info(f"Found {len(report['button_handlers'])} button handlers")
    logger.info(f"Detected {len(report['issues'])} potential issues")
    
    # Display issues
    if report['issues']:
        logger.info("\n--- Potential Issues ---")
        for issue in report['issues']:
            logger.warning(f"⚠️ {issue['severity']} - {issue['file']}: {issue['issue']}")
    
    # Save detailed report to file
    try:
        with open('event_handler_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        logger.info("\nDetailed report saved to 'event_handler_report.json'")
    except Exception as e:
        logger.error(f"Error saving report: {str(e)}")
    
    # Specific button functionality checks and recommendations
    logger.info("\n--- Button Functionality Check ---")
    
    # Check for common button issues
    check_card_actions()
    check_audio_controls()
    check_form_submissions()
    
    logger.info("\nEvent handler inspection complete!")

def check_card_actions():
    """Check specific card action buttons that may have issues"""
    if os.path.exists('templates/notes/list.html'):
        with open('templates/notes/list.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'card-footer' in content and 'btn-group' in content:
            if 'data-bs-toggle="modal"' in content:
                logger.info("✅ Note delete buttons using Bootstrap modal pattern correctly")
            else:
                logger.warning("⚠️ Note action buttons may have issues with modal triggering")

def check_audio_controls():
    """Check audio recording controls"""
    if os.path.exists('templates/notes/new.html'):
        with open('templates/notes/new.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'startRecording' in content and 'stopRecording' in content:
            if 'disabled' in content:
                logger.info("✅ Audio recording buttons using disabled state correctly")
            else:
                logger.warning("⚠️ Audio recording buttons may need disabled state management")

def check_form_submissions():
    """Check form submission handlers"""
    logger.info("Checking form submission handlers...")
    forms_checked = 0
    
    for root, _, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if '<form' in content:
                        forms_checked += 1
                        if 'onsubmit' in content or 'preventDefault' in content:
                            logger.info(f"✅ Form in {file_path} has submission handling")
                        else:
                            logger.warning(f"⚠️ Form in {file_path} may lack client-side validation")
                            
                except Exception as e:
                    logger.error(f"Error checking {file_path}: {str(e)}")
    
    logger.info(f"Checked {forms_checked} forms")

if __name__ == "__main__":
    main()
