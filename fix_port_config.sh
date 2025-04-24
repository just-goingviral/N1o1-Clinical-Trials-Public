#!/bin/bash
# Fix port configuration issues
# Usage: ./fix_port_config.sh

echo "Starting port configuration fix process..."

# Make sure we're using port 5000 consistently throughout the application
# This helps ensure consistency between local development and production

# Check if there are hardcoded ports other than 5000
echo "Checking for hardcoded ports..."
grep -r "app.run" --include="*.py" . | grep -v "5000" || echo "No hardcoded app.run ports found."
grep -r "port=" --include="*.py" . | grep -v "5000" || echo "No hardcoded port= parameters found."
grep -r "bind" --include="*.py" . | grep -v "5000" || echo "No hardcoded bind parameters found."

# Fix main.py if it exists
if [ -f main.py ]; then
    echo "Updating port configuration in main.py..."
    # Ensure we're using 0.0.0.0 and port 5000 from environment variable
    sed -i 's/app.run(host=.*/app.run(host='\''0.0.0.0'\'', port=int(environ.get('\''PORT'\'', 5000)), debug=False)/' main.py || echo "No changes needed in main.py app.run"
fi

# Fix app.py if it exists
if [ -f app.py ]; then
    echo "Updating port configuration in app.py..."
    # Ensure we're using 0.0.0.0 and port 5000 from environment variable
    sed -i 's/app.run(host=.*/app.run(host='\''0.0.0.0'\'', port=int(environ.get('\''PORT'\'', 5000)), debug=False)/' app.py || echo "No changes needed in app.py app.run"
fi

# Create a PORT environment variable if it doesn't exist
if [ -z "$PORT" ]; then
    echo "Setting PORT environment variable to 5000"
    export PORT=5000
fi

echo "Port configuration fix complete."
echo "Remember to restart your application for changes to take effect."