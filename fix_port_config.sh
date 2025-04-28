#!/bin/bash
# Fix port configuration issues in workflow
# This script directly modifies workflow tasks to use a hardcoded port

echo "===== N1O1 Clinical Trials Port Configuration Fix ====="

# Make sure there's a hardcoded port in the environment
export PORT=5000
echo "PORT environment variable set to 5000"

# Create a wrapper script specifically for the workflow
cat > workflow_launcher.sh << 'EOF'
#!/bin/bash

# Always use port 5000 regardless of environment variables
# This ensures the workflow doesn't try to use an empty port
PORT=5000

# Output diagnostic information
echo "N1O1 Clinical Trials starting on port $PORT"
echo "Working directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Process ID: $$"

# Run gunicorn with the hardcoded port
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
EOF

# Make the script executable
chmod +x workflow_launcher.sh

echo "Created workflow_launcher.sh with hardcoded port 5000"
echo ""
echo "IMPORTANT: Update your workflow configuration to use:"
echo "./workflow_launcher.sh"
echo "instead of the current gunicorn command"
echo ""
echo "Port configuration fix complete!"