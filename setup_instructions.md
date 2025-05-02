# N1O1 Clinical Trials - Setup Instructions

## Current Status

The N1O1 Clinical Trials application has been developed with the following features:

- Simulation of nitrite, cGMP, and vasodilation dynamics
- Interactive data visualization with Chart.js
- Patient management system
- Clinical notes with AI assistance
- Mobile-friendly responsive design
- Offline capabilities with local data caching

However, there are currently deployment issues with the Replit workflow system. The application runs correctly when started directly but fails to start through the workflow.

## How to Run the Application

Since the standard workflow isn't working reliably, we've created several alternative ways to run the application:

### Option 1: Using the Standalone Server

```bash
python start_n1o1_standalone.py
```

This will start a simplified version of the application on port 5003 with basic routes and functionality.

### Option 2: Using the Fixed Workflow Script

```bash
./workflow_fixed.sh
```

This script uses a hardcoded port value (5003) to avoid environment variable issues.

### Option 3: Using the Minimal Flask Server

```bash
python minimal_flask_server.py
```

This starts a minimal Flask server that responds to basic health check endpoints.

## Fixing the Workflow

To fix the workflow configuration:

1. Go to the "Tools" menu in Replit
2. Select "Workflows"
3. Edit the "Start application" workflow
4. Replace the command with one of the following:
   - `python start_n1o1_standalone.py`
   - `./workflow_fixed.sh`
   - `python minimal_flask_server.py`
5. Save the workflow

## Known Issues

- The workflow system in Replit sometimes fails to correctly pass environment variables (especially `$PORT`)
- The application occasionally times out during initialization in the workflow system
- If you encounter a "not a valid port number" error, use one of the alternative startup methods listed above

## Additional Resources

- FINAL_DEPLOYMENT_FIX.md - Details on the deployment fixes applied
- new_workflow.toml - Example workflow configuration with hardcoded port
- WORKFLOW_FIXED_COMMAND.txt - The recommended workflow command
