
#!/bin/bash
# Fix port configuration in all relevant files

echo "N1O1 Clinical Trials - Port Configuration Fix"
echo "============================================="

# Replace hardcoded port in .replit file
if [ -f .replit ]; then
  echo "Updating .replit file..."
  sed -i 's/--bind 0.0.0.0:5000/--bind 0.0.0.0:$PORT/g' .replit
  echo "✅ .replit updated"
fi

# Replace hardcoded port in Procfile
if [ -f Procfile ]; then
  echo "Updating Procfile..."
  sed -i 's/--bind 0.0.0.0:5000/--bind 0.0.0.0:$PORT/g' Procfile
  echo "✅ Procfile updated"
fi

# Create run.sh with PORT environment variable
echo "Creating run.sh script..."
cat > run.sh << 'EOF'
#!/bin/bash
export PORT=${PORT:-5000}
echo "Starting server on port $PORT"
gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app
EOF

# Make the script executable
chmod +x run.sh
echo "✅ run.sh created and made executable"

# Set PORT environment variable for current session
export PORT=5000
echo "✅ PORT environment variable set to 5000 for current session"

echo "✅ Port configuration fixed"
echo "Run your application using the 'Run' button, or execute: ./run.sh"
