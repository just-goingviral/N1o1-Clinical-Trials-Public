# Fixing the "Too Many Redirects" Issue with Netlify

This guide provides solutions for the blank screen and redirect loop issues you're experiencing with your Netlify site `neral-kataifi-590c5c.netlify.app`.

## Understanding the Problem

The blank screen you're seeing is likely caused by one of these issues:

1. **Redirect Loop**: Your browser is caught in an infinite loop of redirects between HTTP and HTTPS
2. **CORS Issues**: Security restrictions blocking cross-origin content
3. **Deployment Failure**: Site files not properly deployed to Netlify

## Solutions

### 1. Fix Redirect Loops

#### Option A: Use the Fix Script

Run the provided script to automatically create the necessary configuration files:

```bash
chmod +x fix_netlify_domain.sh
./fix_netlify_domain.sh
```

Then redeploy your site on Netlify.

#### Option B: Manual Configuration

Create a `_redirects` file in your site's root with these contents:

```
# Netlify redirects file to fix blank screens and redirect loops
http://neral-kataifi-590c5c.netlify.app/*  /:splat  200
https://neral-kataifi-590c5c.netlify.app/* /:splat  200

# Handle any other domains/subdomains
/*  /index.html  200
```

### 2. Disable Force HTTPS Temporarily

In your Netlify dashboard:
1. Go to Site settings > Domain management
2. Find the "HTTPS" section
3. Temporarily disable "Force HTTPS"
4. Test your site with HTTP URLs
5. Re-enable once fixed

### 3. Check for Meta Redirects

Ensure your HTML doesn't contain problematic meta tags:

```html
<!-- Remove or modify any tags like this: -->
<meta http-equiv="refresh" content="0;url=https://...">
```

### 4. Clear Browser Cache & Cookies

Try accessing your site:
1. In a private/incognito window
2. After clearing cookies for the domain
3. In a different browser

### 5. Check Request Headers

Use browser dev tools (Network tab) to examine request/response headers:
1. Look for any `X-Forwarded-Proto` issues
2. Check for unusual redirect responses (3xx status codes)

## Testing Your Fix

After implementing the fixes:

1. Wait for Netlify to deploy the changes (usually 1-2 minutes)
2. Access your site in a private browser window
3. Try both HTTP and HTTPS versions of the URL
4. Check the browser console for any remaining errors

## Getting More Help

If these solutions don't resolve the issue:

1. Check your Netlify deploy logs for errors
2. Examine your Flask application logs
3. Consider simplifying your app temporarily to isolate the issue

## Preventative Measures for Future Builds

- Always use relative URLs in your application
- Avoid hardcoding protocol (http/https) in URLs
- Test with site preview URLs before deploying to production
- Use Netlify's Functions or Edge Handlers for complex routing needs