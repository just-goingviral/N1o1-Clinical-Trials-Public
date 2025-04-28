#!/bin/bash
# Fix Netlify domain redirect issues

DOMAIN="neral-kataifi-590c5c.netlify.app"
echo "Fixing redirect issues for $DOMAIN"

# Create _redirects file for Netlify
cat > _redirects << EOL
# Netlify redirects file to fix blank screens and redirect loops
# Force specific rules to avoid redirect loops
http://$DOMAIN/*  /:splat  200
https://$DOMAIN/* /:splat  200

# Handle any other domains/subdomains
/*  /index.html  200
EOL

echo "Created _redirects file"

# Check if we have a netlify.toml file
if [ -f netlify.toml ]; then
  echo "Found netlify.toml, updating it"
  
  # Backup the original
  cp netlify.toml netlify.toml.bak
  
  # Check if it already has redirects section
  if grep -q "\[\[redirects\]\]" netlify.toml; then
    echo "netlify.toml already has redirects, not modifying"
  else
    # Add redirects section
    cat >> netlify.toml << EOL

# Fix for redirect loops
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  force = false
EOL
    echo "Added redirects to netlify.toml"
  fi
else
  # Create a new netlify.toml file
  cat > netlify.toml << EOL
# Netlify configuration
[build]
  publish = "."
  command = ""

# Fix for redirect loops  
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  force = false
EOL
  echo "Created new netlify.toml file"
fi

# Instruct user on next steps
echo ""
echo "=== Next Steps ==="
echo "1. Deploy these changes to your Netlify site"
echo "2. In Netlify settings, temporarily disable 'Force HTTPS'"
echo "3. Clear your browser cache or try in a private browsing window"
echo "4. If issues persist, check Netlify deploy logs for errors"
echo ""