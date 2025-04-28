#!/usr/bin/env python3
"""
Fix incorrect url_for calls in routes/notes_routes.py
"""

import re

def fix_notes_routes():
    # Read the file
    with open('routes/notes_routes.py', 'r') as f:
        content = f.read()
    
    # Replace any url_for( , _external=True) with url_for('notes.list_notes', _external=True)
    content = re.sub(r"url_for\(\s*,\s*_external=True\)", 
                    "url_for('notes.list_notes', _external=True)", 
                    content)
    
    # Write the corrected file
    with open('routes/notes_routes.py', 'w') as f:
        f.write(content)
    
    print("Fixed notes_routes.py url_for errors")

if __name__ == "__main__":
    fix_notes_routes()