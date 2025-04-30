# N1O1 Clinical Trials - Workflow Configuration Fix

## The Issue
The current workflow is failing with the error:
```
Error: '' is not a valid port number.
```

This happens because the workflow is trying to use the `$PORT` environment variable, but it's empty.

## How to Fix It

### Option 1: Update the Workflow Command in Replit UI
1. Click on the "Run" button at the top of the screen
2. Click the gear icon (⚙️) next to the "Start application" workflow
3. Replace the command with this fixed version:
   ```
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```
4. Click "Save changes"
5. Click "Run" to start the application

### Option 2: Run the Fixed Command Script
If you'd rather not change the workflow configuration, you can run this script directly:
```
./fixed_workflow_command.sh
```

## Port Assignment Explained
- The script uses port 5000 hardcoded directly in the command
- This bypasses the need for the PORT environment variable
- By using a fixed port number, we ensure the application starts consistently every time

Note: This fix addresses only the workflow startup issue. The "too many redirects" issue has been fixed separately by modifying the URL generation logic in main.py.