# How to Fix Workflow Issues in N1O1 Clinical Trials

If you're experiencing issues with the Replit workflow, try these solutions:

## 1. Use a Direct Starter Script

```bash
./start_gunicorn.sh
```

This script bypasses all workflow configuration and starts the application directly with a hardcoded port number.

## 2. Use the Python Direct Starter

```bash
python start_direct.py
```

This is another option that uses Python's built-in development server instead of Gunicorn.

## 3. Set PORT Environment Variable Manually

```bash
export PORT=5003
gunicorn --bind 0.0.0.0:$PORT main:app
```

## 4. Check Common Issues

- The most common issue is the missing PORT environment variable
- Another issue is route conflicts between different startup scripts
- Browser cache can sometimes cause problems - try clearing your browser cache

## 5. UI Button Issues

If buttons aren't working properly:

- We've added a button-fix.js script that repairs common Bootstrap button issues
- Check the JavaScript console for any errors
- Try clicking the area around the button if the button itself isn't responding
- For tab navigation issues, try using the button-fix.js manual tab switcher

## Using the Research Insight Generator

The new Research Insight Generator feature is available at:

```
/research/insights
```

You can access it directly from the dashboard via the new Research Insights card.
