#!/bin/bash
# Direct start script for N1O1 Clinical Trials
# This script handles common startup issues and forces correct settings

echo "N1O1 Clinical Trials - Fixed Startup Script"
echo "===================================="

# Make sure templates directory exists
if [ ! -d "./templates" ]; then
  mkdir -p ./templates
  echo "Created templates directory"
fi

# Create a minimal index template if it doesn't exist
if [ ! -f "./templates/index.html" ]; then
  cat > ./templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h1>N1O1 Clinical Trials</h1>
                    </div>
                    <div class="card-body">
                        <h2>System Status: Online</h2>
                        <p>The application is running correctly.</p>
                        <p>This is a minimal working version of the application.</p>
                        <div class="mt-4">
                            <a href="/system/health" class="btn btn-info me-2">System Health</a>
                            <a href="/ping" class="btn btn-secondary">Ping Test</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
EOF
  echo "Created minimal index.html template"
fi

# Create error template if it doesn't exist
if [ ! -f "./templates/error.html" ]; then
  cat > ./templates/error.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <div class="card border-danger">
                    <div class="card-header bg-danger text-white">
                        <h2>Error</h2>
                    </div>
                    <div class="card-body">
                        <p>An error occurred: {{ error }}</p>
                        <a href="/" class="btn btn-primary">Return to Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
EOF
  echo "Created error.html template"
fi

# Kill any existing processes on port 5000
echo "Cleaning up any existing processes..."
fuser -k 5000/tcp 2>/dev/null || echo "No existing process on port 5000"
sleep 2

# Set environment variables correctly
export PORT=5000
export FLASK_DEBUG=0
export FLASK_ENV=production
export SESSION_COOKIE_SECURE=False
export PREFERRED_URL_SCHEME=http
export SERVER_NAME=""

echo "Starting application with fixed settings"
echo "PORT=$PORT"
echo ""
echo "Running on: http://localhost:5000/"
echo ""

# Start gunicorn with fixed app and fixed port
exec gunicorn --bind 0.0.0.0:5000 --reload --timeout 300 --workers 1 --log-level info fixed_main:app