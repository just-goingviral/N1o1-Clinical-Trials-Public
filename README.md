# NO Dynamics Simulator

A comprehensive Python application for simulating nitrite, cGMP, and vasodilation dynamics. This tool is designed for Dr. Nathan Bryan's clinical trials to model plasma nitrite (NO₂⁻) dynamics after sodium nitrite supplementation.

## Features

- **ODE-based Pharmacokinetic Model**: Accurately simulates plasma nitrite kinetics
- **Interactive Visualization**: Real-time simulation results with dynamic charts
- **Parameter Customization**: Adjust all relevant physiological parameters
- **Statistical Analysis**: Comprehensive analysis of nitrite kinetics
- **Parameter Optimization**: Fit simulation to experimental data
- **Sensitivity Analysis**: Evaluate impact of parameter changes
- **Command-line Interface**: Automation and batch processing capabilities
- **Electron Desktop App**: Cross-platform graphical interface

## Installation

### Prerequisites

- Python 3.8 or higher
- NumPy, SciPy, Matplotlib, Pandas
- Flask (for web interface)
- Electron (for desktop application)

### Command-line Tool

```bash
# Clone the repository
git clone https://github.com/yourusername/no-dynamics-simulator.git
cd no-dynamics-simulator

# Install Python dependencies
pip install numpy scipy matplotlib pandas flask statsmodels
