# N1O1 Clinical Trials - Fixing "Too Many Redirects" Issue

## Overview

This guide addresses the "too many redirects" issue that can occur when deploying the N1O1 Clinical Trials application. The problem typically happens due to inconsistencies in URL generation, cookie settings, and proxy handling.

## Root Causes

The redirect loop can be caused by:

1. **Inconsistent URL scheme handling**: When the application generates URLs with inconsistent schemes (http vs https)
2. **Cookie security settings**: When cookie settings are not compatible with the request scheme
3. **Server name configuration**: When the server name is hardcoded or not properly detecting the request domain
4. **Proxy header handling**: When proxy headers like X-Forwarded-Proto are not properly processed

## Applied Fixes

We've applied the following fixes to resolve the issue:

1. **Simplified URL generation**: Modified `safe_url_for` function to use a consistent HTTP scheme
2. **Updated cookie settings**: Set `SESSION_COOKIE_SECURE = False` to allow cookies over HTTP
3. **Set URL scheme**: Enforced `PREFERRED_URL_SCHEME = 'http'` consistently
4. **Simplified proxy handling**: Reduced ProxyFix middleware configuration to essential parameters
5. **Created fixed startup script**: Added `start_fixed_app.sh` with correct environment settings

## How to Use the Fix

### Method 1: Run the Fixed Application Script

```bash
./start_fixed_app.sh
```

This script:
- Sets all required environment variables
- Uses a fixed port (5000)
- Applies the correct configuration to prevent redirect loops

### Method 2: Update Your Workflow Configuration

Manually update your workflow configuration in the Replit UI to use:

```
PORT=5000 PREFERRED_URL_SCHEME=http SESSION_COOKIE_SECURE=False SERVER_NAME= gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Verifying the Fix

After applying these fixes, you should be able to:

1. Navigate between pages without encountering redirect loops
2. Access the application using both Replit's domain and custom domains
3. Have consistent URL generation across all application routes

## Technical Details

### Key Changes in main.py

```python
# Updated safe_url_for function
def safe_url_for(endpoint, **kwargs):
    """Generate URLs with a consistent scheme to prevent redirect loops"""
    # Always use HTTP for external URLs (if not explicitly specified)
    if '_external' in kwargs and kwargs['_external'] and '_scheme' not in kwargs:
        kwargs['_scheme'] = 'http'
    
    return url_for(endpoint, **kwargs)

# Updated ProxyFix configuration
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,    # Handle X-Forwarded-Proto (minimal configuration)
    x_host=1      # Handle X-Forwarded-Host (minimal configuration)
)
```

### Environment Variable Settings

```
PORT=5000
PREFERRED_URL_SCHEME=http
SESSION_COOKIE_SECURE=False
SERVER_NAME=
```

## Contact

If you continue to experience issues, please contact support.