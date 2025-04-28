#!/usr/bin/env python3
"""
Fix missing commas in url_for/_external=True parameters throughout the codebase
"""
import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_url_for_syntax(file_path):
    """Fix missing commas in url_for calls with _external=True parameter"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find url_for followed by arguments missing comma before _external=True
        pattern = r"url_for\(['\"][^'\"]+['\"](\s+)_external=True\)"
        
        # Check if pattern exists in file
        if not re.search(pattern, content):
            return 0, []
        
        # Replace with comma before _external=True
        fixed_content = re.sub(pattern, r"url_for(\1, _external=True)", content)
        
        # Save the fixed content
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        # Count number of fixes (occurrences of pattern)
        count = len(re.findall(pattern, content))
        
        # Find the line numbers
        lines = content.split('\n')
        line_fixes = []
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                line_fixes.append(i + 1)
        
        return count, line_fixes
    except Exception as e:
        logger.error(f"Error fixing {file_path}: {e}")
        return 0, []

def scan_directory(root_dir='.'):
    """Scan directory for Python files and fix them"""
    total_fixes = 0
    files_fixed = 0
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Skip virtual environments and version control directories
                if '/venv/' in file_path or '/.git/' in file_path:
                    continue
                
                # Fix syntax in file
                fixes, line_fixes = fix_url_for_syntax(file_path)
                
                if fixes > 0:
                    files_fixed += 1
                    total_fixes += fixes
                    logger.info(f"Fixed {fixes} issues in {file_path} at lines {line_fixes}")
    
    return total_fixes, files_fixed

def main():
    """Main function"""
    logger.info("Starting syntax fix script")
    
    # Fix url_for/_external syntax
    total_fixes, files_fixed = scan_directory()
    
    if total_fixes > 0:
        logger.info(f"Fixed {total_fixes} syntax issues in {files_fixed} files")
    else:
        logger.info("No syntax issues found")
    
    logger.info("Syntax fix script completed")

if __name__ == "__main__":
    main()