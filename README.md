# N1O1 Clinical Trials

A comprehensive Python application for advanced scientific research simulation, specializing in nitrite, cGMP, and vasodilation dynamics with interactive data management and visualization capabilities.

## Running the Application

There are multiple ways to start the N1O1 Clinical Trials application:

### Method 1: Using the start_clean.sh script (Recommended)

```bash
./start_clean.sh
```

This script kills any existing processes on port 5000, waits for the port to be released, and starts the application with a fixed port configuration.

### Method 2: Using the run_port_fixed.sh script

```bash
./run_port_fixed.sh
```

A simpler script that starts the application with fixed port 5000.

### Method 3: Directly with Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --timeout 300 --workers 1 main:app
```

### Method 4: Using the Replit Run button

The application is configured to start when you click the "Run" button in Replit, but this may encounter issues with the port configuration. If the Run button doesn't work, use one of the above methods.

## Features

- Interactive plasma nitrite simulation
- Clinical trial participant management
- Visualization of nitrite, cGMP, and vasodilation dynamics
- AI-powered clinical assistant (N1o1ai)
- Clinical notes with voice recording capability
- Patient education resources
- Statistical analysis tools

## Technical Information

- **Flask**: Web application framework
- **Electron**: Desktop interface
- **Chart.js**: Data visualization
- **Python Scientific Libraries**: NumPy, SciPy, Pandas, etc.
- **Bootstrap**: Responsive design
- **AI Integration**: OpenAI and Anthropic Claude for clinical workflows

## Deployment

The application is configured for deployment on Replit with automatic port configuration.

## Troubleshooting

### Application Not Starting

If you encounter issues with the application not starting:

1. Verify that no other process is running on port 5000
2. Ensure that all script files are executable (`chmod +x script_name.sh`)
3. Check the application logs for any specific error messages

### Redirect Loops

If you encounter redirect loops or login issues:

1. Clear your browser cookies and cache
2. The application uses HTTP cookies (not HTTPS) for better compatibility
3. Check that your browser allows third-party cookies
4. Use the application's direct URL rather than through a proxy

### Custom Domain Issues

For custom domain configuration, see the [Custom Domain Guide](CUSTOM_DOMAIN_GUIDE.md).