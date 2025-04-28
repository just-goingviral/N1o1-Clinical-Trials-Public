#!/bin/bash
# Fix custom domain deployment issues
echo "=== N1O1 Clinical Trials - Custom Domain Fix Tool ==="
echo "This script fixes common issues with custom domain deployments."
echo

# 1. Fix session directory permissions
echo "1. Checking and fixing session directory permissions..."
mkdir -p flask_session
chmod 755 flask_session
echo "✓ Session directory permissions fixed"

# 2. Clear any existing session files to prevent redirect loops
echo "2. Clearing existing session files..."
rm -f flask_session/*
echo "✓ Session files cleared"

# 3. Set the REPLIT_DEPLOYMENT environment variable for proper cookie config
echo "3. Setting deployment environment variables..."
echo "export REPLIT_DEPLOYMENT=True" > .env
echo "✓ Environment variables set"

# 4. Update the proxy fix in main.py to handle more proxies
echo "4. Checking ProxyFix configuration..."
if grep -q "x_for=1" main.py; then
    echo "✓ ProxyFix already configured"
else
    echo "Warning: ProxyFix not found. Please check main.py manually."
fi

# 5. Update Procfile to use our fixed startup script
echo "5. Updating Procfile..."
echo "web: REPLIT_DEPLOYMENT=True ./start_application.sh" > Procfile
echo "✓ Procfile updated"

# 6. Make sure the start script exists and is executable
echo "6. Checking startup script..."
if [ -f "start_application.sh" ]; then
    chmod +x start_application.sh
    echo "✓ Startup script is ready"
else
    echo "ERROR: start_application.sh not found!"
    echo "Creating default startup script..."
    cat > start_application.sh << 'EOF'
#!/bin/bash
# This script ensures the application starts with proper port configuration
export PORT=${PORT:-5000}
echo "Setting PORT environment variable to $PORT"

# Enable deployment mode for secure cookies
export REPLIT_DEPLOYMENT=True

# Run gunicorn with explicit port binding
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app
EOF
    chmod +x start_application.sh
    echo "✓ Created default startup script"
fi

echo
echo "=== Fix complete! ==="
echo "To restart your application with these fixes, run:"
echo "  ./start_application.sh"
echo 
echo "For deployment, make sure to deploy with the updated Procfile."