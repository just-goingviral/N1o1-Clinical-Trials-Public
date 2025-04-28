# N1O1 Clinical Trials - Custom Domain Deployment Guide

This guide helps you fix the "too many redirects" error that can occur when deploying the application with a custom domain.

## Quick Fix

Run the automated fix script:

```bash
chmod +x fix_domain.sh
./fix_domain.sh
```

Then redeploy your application.

## Understanding the Issue

The "too many redirects" error occurs because of three main issues:

1. **Session Cookie Configuration**: When using a custom domain with HTTPS, cookies need to be properly configured with the `Secure` flag.

2. **Proxy Configuration**: The application needs to properly handle proxy headers when behind Replit's load balancer.

3. **Redirect Loop Protection**: The application's redirect loop protection needs special handling for custom domains.

## Manual Fixes

If the automatic script doesn't work, you can apply these fixes manually:

### 1. Update Session Cookie Settings

In `main.py`, find and modify the session cookie configuration:

```python
# Set session cookie security based on environment
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('REPLIT_DEPLOYMENT', False) == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None
```

### 2. Clear Existing Session Files

Remove any existing session files to ensure a clean start:

```bash
rm -f flask_session/*
```

### 3. Update the Procfile

Ensure your Procfile sets the correct environment variable:

```
web: REPLIT_DEPLOYMENT=True ./start_application.sh
```

### 4. Update the Start Script

Make sure `start_application.sh` includes:

```bash
#!/bin/bash
export PORT=${PORT:-5000}
export REPLIT_DEPLOYMENT=True
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app
```

## Verification

After making these changes:

1. Run the application locally with `./start_application.sh`
2. Verify it works in the Replit environment
3. Deploy the application
4. Test your custom domain

## Troubleshooting

If you still experience issues:

1. Check the application logs for specific error messages
2. Verify your DNS settings for the custom domain
3. Try using a private/incognito browser window to avoid cached cookies
4. Clear your browser cookies and cache

For persistent issues, you may need to examine the request/response cycle using browser developer tools to identify where the redirect loop is occurring.