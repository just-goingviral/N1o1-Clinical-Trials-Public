
#!/bin/bash
# Fix domain configuration issues

echo "N1O1 Clinical Trials - Domain Configuration Fix"
echo "=============================================="

# Check for needed commands
command -v dig >/dev/null 2>&1 || { echo "Error: 'dig' command not found. Installing..."; apt-get update && apt-get install -y dnsutils; }

# Get custom domain
if [ -z "$1" ]; then
  read -p "Enter your custom domain (e.g., trials.n1o1app.com): " CUSTOM_DOMAIN
else
  CUSTOM_DOMAIN="$1"
fi

echo "Working with domain: $CUSTOM_DOMAIN"

# Check DNS records
echo "Checking DNS A record..."
DIG_RESULT=$(dig +short A $CUSTOM_DOMAIN)
if [ -n "$DIG_RESULT" ]; then
  echo "✅ A record found: $DIG_RESULT"
else
  echo "❌ No A record found for $CUSTOM_DOMAIN"
  echo "   Please add an A record in your domain registrar pointing to Replit's IP."
fi

echo "Checking DNS TXT record..."
DIG_TXT=$(dig +short TXT $CUSTOM_DOMAIN)
if [ -n "$DIG_TXT" ]; then
  echo "✅ TXT record found: $DIG_TXT"
else
  echo "❌ No TXT record found for $CUSTOM_DOMAIN"
  echo "   Please add the TXT record provided by Replit for domain verification."
fi

# Fix port configuration
echo -e "\nFixing port configuration..."

# Create or update run.sh
echo "Updating run.sh script..."
cat > run.sh << 'EOF'
#!/bin/bash
export PORT=${PORT:-5000}
echo "Starting server on port $PORT for domain $REPLIT_DEPLOYMENT_DOMAIN"
gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app
EOF

chmod +x run.sh
echo "✅ run.sh updated and made executable"

# Update .replit workflow
echo "Checking .replit workflow..."
if grep -q "0.0.0.0:5000" .replit; then
  echo "⚠️ Found hardcoded port in .replit, this should be updated in the web interface"
  echo "   Go to the 'Workflow' tab in your repl and update the Run command to use \$PORT instead of 5000"
fi

# Update Procfile
echo "Updating Procfile..."
echo "web: gunicorn --bind 0.0.0.0:\$PORT --timeout 300 --workers 1 --keep-alive 120 --log-level info main:app" > Procfile
echo "✅ Procfile updated"

# Add a check for custom domain in health endpoint
echo "Enhancing health endpoint for domain diagnosis..."
if grep -q "system/health" main.py; then
  # Try to update the health endpoint to show domain info
  if ! grep -q "request.host" main.py; then
    HEALTH_LINE=$(grep -n "def system_health" main.py | cut -d':' -f1)
    if [ -n "$HEALTH_LINE" ]; then
      # Insert domain info in the health response
      HEALTH_DICT_LINE=$((HEALTH_LINE + 5))
      sed -i "${HEALTH_DICT_LINE}s/}/    \"domain\": request.host,\n        \"request_url\": request.url,\n    }/" main.py
      echo "✅ Enhanced health endpoint with domain diagnostics"
    fi
  else
    echo "✅ Health endpoint already includes domain info"
  fi
else
  echo "⚠️ Could not locate health endpoint in main.py"
fi

echo -e "\n✅ Domain configuration fixes applied"
echo "Next steps:"
echo "1. Redeploy your application in the Deployments tab"
echo "2. If using Cloudflare, make sure SSL/TLS setting is 'Full' (not Proxied)"
echo "3. Test both your Replit domain and custom domain"
echo "4. Run 'python check_domain.py $CUSTOM_DOMAIN' to diagnose any remaining issues"
