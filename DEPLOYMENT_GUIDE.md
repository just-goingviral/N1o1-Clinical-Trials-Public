# N1O1 Clinical Trials Deployment Guide

This guide explains how to successfully deploy the N1O1 Clinical Trials application.

## Common Issues Fixed

This application includes several scripts to fix common deployment issues:

### 1. Redirect Loops and Cookie Issues

If you encounter redirect loops or cookie-related errors:

```bash
# Run the redirect issues fix script
python fix_redirects_simple.py
```

This script:
- Restores from backup if available
- Applies critical cookie settings
- Sets SESSION_COOKIE_SECURE=False
- Sets PREFERRED_URL_SCHEME='http'
- Sets SERVER_NAME=None

### 2. Port Configuration Issues

If you encounter port-related errors:

```bash
# Run the port configuration fix script
./fix_port_config.sh
```

This creates `workflow_launcher.sh` which:
- Uses hardcoded port settings
- Tries multiple ports if needed
- Properly handles process cleanup

### 3. Workflow Configuration Issues

If workflow fails to start:

```bash
# Run the workflow fix script
./fix_workflow.sh
```

This creates `reliable_workflow.sh` which:
- Uses fixed hardcoded settings for everything
- Avoids all environment variable references
- Ensures proper process cleanup

## Deployment Scripts

For production deployment:

```bash
# Prepare for deployment
./deploy.sh

# Then deploy using Replit's deployment system
```

This script:
- Applies all necessary fixes
- Creates optimal environment variables
- Sets up the correct Procfile

## Startup Options

Multiple startup scripts are available:

- `./fast_start.sh` - Optimized startup using environment variables
- `./run_with_hardcoded_port.sh` - Tries multiple ports sequentially
- `./reset_and_start.sh` - Comprehensive reset and startup
- `./reliable_workflow.sh` - Hardcoded settings for workflow use

## Troubleshooting

If the application still won't start:

1. Check logs for specific errors
2. Kill any existing processes: `fuser -k 5000/tcp`
3. Clear session files: `rm -f flask_session/*`
4. Try an alternate port: `export PORT=8080 && ./fast_start.sh`
5. Use the hardcoded port script: `./run_with_hardcoded_port.sh`

## Environment Variables

A `.env` file has been created with optimal settings. Use `source ./load_env.sh` to load these variables.

Key variables:
- `PORT=5000`
- `SESSION_COOKIE_SECURE=False`
- `PREFERRED_URL_SCHEME=http`
- `SERVER_NAME=""` (empty string)