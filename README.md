# N1O1 Clinical Trials

A comprehensive Python application for advanced scientific research simulation, specializing in nitrite, cGMP, and vasodilation dynamics with interactive data management and visualization capabilities.

## Running the Application

There are multiple ways to start the N1O1 Clinical Trials application:

### Method 1: Using the start_application.sh script (Recommended)

```bash
./start_application.sh
```

This script sets the PORT environment variable and runs the application with Gunicorn.

### Method 2: Directly with Gunicorn

```bash
export PORT=5000 && gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app
```

### Method 3: Using the Replit Run button

The application is configured to start when you click the "Run" button in Replit.

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

If you encounter issues with the application not starting:

1. Check if the PORT environment variable is set correctly
2. Ensure that the start_application.sh script is executable (chmod +x start_application.sh)
3. Verify that no other process is running on port 5000
4. Check the application logs for any specific error messages