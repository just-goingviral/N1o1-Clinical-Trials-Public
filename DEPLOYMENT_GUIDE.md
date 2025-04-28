# N1O1 Clinical Trials Deployment Guide

This guide explains how to successfully deploy the N1O1 Clinical Trials application on both Replit and custom domains.

## Cross-Domain Deployment Fix

The application has been updated to work correctly on both Replit's internal domain (.repl.co) and custom domains without redirect loops or URL generation issues.

Key improvements:
- Dynamic URL scheme detection from proxy headers
- Intelligent `safe_url_for()` helper function that respects the deployment environment
- Proper handling of `X-Forwarded-Proto` headers for HTTPS detection
- Avoidance of hardcoded URL schemes in redirects
- Server name determined from request, not configuration

## Quick Start

The fastest way to deploy the application is:

```bash
# Start the application with our fixed workflow script
chmod +x workflow_fixed.sh
./workflow_fixed.sh
```

This script:
- Uses a hardcoded port (5000) that won't fail
- Properly cleans up existing processes
- Starts gunicorn with our fixed main.py

## Verification

To verify your deployment is working correctly:

```bash
# Install verification script dependencies
pip install requests

# Run the verification script
python verify_deployment.py
```

For a custom domain:

```bash
python verify_deployment.py --domain yourdomain.com
```

The script checks:
1. Basic connectivity (/ping endpoint)
2. System health (/system/health endpoint)  
3. Redirect handling (/patient → /patients)

## Deploying to Production

When deploying to production:

1. Ensure `PREFERRED_URL_SCHEME` environment variable is set correctly:
   - For HTTPS sites: `export PREFERRED_URL_SCHEME=https`
   - For HTTP sites: `export PREFERRED_URL_SCHEME=http`

2. The application automatically handles secure connection detection, but you can override:
   ```
   export SESSION_COOKIE_SECURE=True  # For HTTPS only
   ```

3. Use `workflow_fixed.sh` for reliable starting, or add this to your Procfile:
   ```
   web: gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 main:app
   ```

## Troubleshooting

If the application still has deployment issues:

1. Check if ProxyFix is properly configured for your environment
2. Verify the application is receiving proper forwarded headers
3. Look for hardcoded URL schemes in route files
4. Try running the app with `debug=True` temporarily to see detailed errors
5. Check if cookie attributes are compatible with your deployment (SameSite, Secure flags)

## Technical Details

The deployment fixes work by:

1. Using ProxyFix middleware to handle proxy-forwarded headers correctly
2. Avoiding `SERVER_NAME` fixed configuration that can cause redirect issues 
3. Injecting `safe_url_for()` into templates to ensure consistent URL generation
4. Making `safe_redirect()` aware of the deployment context
5. Automatically adapting URL scheme based on request headers

For custom domains behind CDNs or load balancers, no additional configuration is needed as the application now correctly handles forwarded headers.