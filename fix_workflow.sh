#!/bin/bash
# Script to fix the Replit workflow configuration

echo "=== N1O1 Clinical Trials - Workflow Fix Tool ==="
echo "This script creates a robust command for the Replit workflow."
echo

# Create a fixed workflow command file
cat > .replit.workflow.fixed << EOF
run = "PORT=5000 gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app"
EOF

echo "Created fixed workflow command."
echo
echo "To fix your workflow configuration:"
echo "1. Click on the 'Run' button dropdown (top center)"
echo "2. Select 'Configure Runs'"
echo "3. Find 'Start application' workflow"
echo "4. Replace the command with:"
echo "   PORT=5000 gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app"
echo "5. Click 'Save changes'"
echo
echo "Alternatively, you can use:"
echo "   ./start_application.sh"
echo
echo "For deployment with custom domains:"
echo "1. Run './fix_domain.sh' first"
echo "2. Deploy your application"
echo "3. Test your custom domain in a private/incognito browser window"