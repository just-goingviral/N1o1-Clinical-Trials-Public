#!/bin/bash
# Fix workflow configuration for reliable startup
# This script patches the workflow configuration issues

echo "===== N1O1 Clinical Trials Workflow Fix ====="

# Create a known good workflow script
cat > reliable_workflow.sh << 'EOF'
#!/bin/bash
# Reliable workflow script with hardcoded settings
# This script ensures the application starts regardless of environment issues

# Always use these fixed settings
FIXED_PORT=5000
FIXED_WORKERS=1
FIXED_TIMEOUT=300

# Diagnostic output
echo "Starting N1O1 Clinical Trials with fixed settings:"
echo "- Port: $FIXED_PORT"
echo "- Workers: $FIXED_WORKERS"
echo "- Timeout: $FIXED_TIMEOUT"

# Attempt to kill any existing process on this port
fuser -k $FIXED_PORT/tcp 2>/dev/null || echo "No existing process on port $FIXED_PORT"
sleep 2

# Use a direct command with all parameters hardcoded - no variables
exec gunicorn --bind 0.0.0.0:5000 --timeout 300 --workers 1 --keep-alive 120 main:app
EOF

# Make it executable
chmod +x reliable_workflow.sh

# Provide guidance message
echo ""
echo "Created reliable_workflow.sh with hardcoded settings"
echo ""
echo "To fix the workflow permanently:"
echo "1. Use this script in your workflow definition: ./reliable_workflow.sh"
echo "2. Or update your .replit workflow to use this exact command:"
echo "   'gunicorn --bind 0.0.0.0:5000 --timeout 300 --workers 1 --keep-alive 120 main:app'"
echo "3. Do not reference the \$PORT variable in the workflow"
echo ""
echo "The application should now start successfully with these changes."