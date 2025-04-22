
"""
Matplotlib Configuration for N1O1 Clinical Trials
Provides a consistent and attractive styling for plots
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def configure_mpl_style():
    """Configure matplotlib with a custom style for N1O1 plots"""
    # Set the style
    plt.style.use('dark_background')
    
    # Configure custom colors
    n1o1_blue = '#3b7eb9'
    n1o1_red = '#e05a47'
    n1o1_green = '#2ecc71'
    n1o1_purple = '#9b59b6'
    
    # Create a custom colormap for NO-related plots
    colors = [(0, n1o1_blue), (0.5, n1o1_purple), (1, n1o1_red)]
    n1o1_cmap = LinearSegmentedColormap.from_list('n1o1_cmap', colors)
    plt.register_cmap(cmap=n1o1_cmap)
    
    # Set default parameters
    mpl.rcParams.update({
        'figure.facecolor': '#121c2c',
        'axes.facecolor': '#16325c',
        'axes.edgecolor': '#3b7eb9',
        'axes.labelcolor': 'white',
        'axes.grid': True,
        'grid.color': 'gray',
        'grid.alpha': 0.3,
        'xtick.color': 'white',
        'ytick.color': 'white',
        'text.color': 'white',
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.facecolor': '#1e293b',
        'legend.edgecolor': '#3b7eb9',
        'savefig.facecolor': '#121c2c',
        'savefig.dpi': 150
    })
    
    return n1o1_cmap

def create_no_stylized_plot(x, y, title="Nitric Oxide Dynamics", xlabel="Time (minutes)", ylabel="Concentration (µM)"):
    """Create a plot with NO-stylized elements"""
    # Configure style
    cmap = configure_mpl_style()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the main data
    ax.plot(x, y, color='#3b7eb9', linewidth=3, alpha=0.8)
    
    # Add a fill between the line and zero
    ax.fill_between(x, y, color='#3b7eb9', alpha=0.2)
    
    # Add NO molecule markers at key points
    # Find peak position
    peak_idx = np.argmax(y)
    
    # Add markers at key positions
    ax.scatter([x[0], x[peak_idx], x[-1]], 
              [y[0], y[peak_idx], y[-1]], 
              color=['#3b7eb9', '#e05a47', '#3b7eb9'], 
              s=[80, 120, 80], 
              zorder=5,
              edgecolor='white',
              linewidth=1.5)
    
    # Add annotations
    ax.annotate('Baseline', (x[0], y[0]), xytext=(10, 10), textcoords='offset points')
    ax.annotate(f'Peak: {y[peak_idx]:.2f} µM', (x[peak_idx], y[peak_idx]), 
                xytext=(10, 10), textcoords='offset points')
    
    # Add a title with styling
    ax.set_title(title, fontsize=16, pad=20, color='white', fontweight='bold')
    
    # Add labels
    ax.set_xlabel(xlabel, fontsize=12, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=12, labelpad=10)
    
    # Add a grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Add a subtle background gradient
    gradient = np.linspace(0, 1, 100).reshape(-1, 1)
    ax.imshow(gradient, aspect='auto', extent=[ax.get_xlim()[0], ax.get_xlim()[1], 
                                              ax.get_ylim()[0], ax.get_ylim()[1]], 
              origin='lower', alpha=0.1, cmap=cmap)
    
    # Improve overall appearance
    fig.tight_layout()
    
    return fig, ax
