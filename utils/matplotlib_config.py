"""
Enhanced matplotlib configuration for scientific visualization
Revolutionary styling for nitric oxide research data presentation
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection

def configure_mpl_style():
    """Configure matplotlib for publication-quality scientific plots"""
    # Scientific color palette optimized for nitric oxide research
    colors = {
        'primary': '#2E3440',      # Nord Polar Night
        'no2': '#5E81AC',          # Nord Frost - for nitrite
        'cgmp': '#A3BE8C',         # Nord Aurora Green - for cGMP
        'vasodilation': '#81A1C1', # Nord Frost Light - for vasodilation
        'background': '#ECEFF4',   # Nord Snow Storm
        'grid': '#D8DEE9',         # Nord Snow Storm Medium
        'text': '#2E3440',         # Nord Polar Night
        'accent': '#BF616A'        # Nord Aurora Red
    }
    
    # Set custom style parameters
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Override with custom parameters
    mpl.rcParams.update({
        # Figure settings
        'figure.figsize': (10, 6),
        'figure.dpi': 100,
        'figure.facecolor': colors['background'],
        'figure.edgecolor': 'none',
        
        # Axes settings
        'axes.facecolor': 'white',
        'axes.edgecolor': colors['grid'],
        'axes.linewidth': 1.0,
        'axes.grid': True,
        'axes.labelcolor': colors['text'],
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 12,
        'axes.labelweight': 'medium',
        
        # Grid settings
        'grid.color': colors['grid'],
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'grid.alpha': 0.7,
        
        # Line settings
        'lines.linewidth': 2.5,
        'lines.antialiased': True,
        
        # Font settings
        'font.family': ['Helvetica Neue', 'Arial', 'sans-serif'],
        'font.size': 11,
        
        # Legend settings
        'legend.frameon': True,
        'legend.facecolor': 'white',
        'legend.edgecolor': colors['grid'],
        'legend.framealpha': 0.9,
        'legend.fontsize': 10,
        
        # Tick settings
        'xtick.color': colors['text'],
        'ytick.color': colors['text'],
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        
        # Save settings
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        'savefig.facecolor': 'white',
        'savefig.edgecolor': 'none'
    })
    
    return colors

def create_gradient_fill(ax, x, y, color, alpha=0.3):
    """Create gradient fill under curve for enhanced visualization"""
    # Create gradient
    z = np.linspace(0, 1, 100).reshape(1, -1)
    extent = [x.min(), x.max(), 0, y.max()]
    
    # Plot gradient
    ax.imshow(z, aspect='auto', cmap=plt.cm.Blues, alpha=alpha, extent=extent)
    
    # Add the actual line on top
    ax.plot(x, y, color=color, linewidth=2.5, zorder=10)
    
    # Fill area under curve
    ax.fill_between(x, 0, y, alpha=alpha/2, color=color)

def add_annotations(ax, x, y, annotations, colors):
    """Add smart annotations to highlight key points"""
    for ann in annotations:
        idx = ann['index']
        ax.annotate(
            ann['text'],
            xy=(x[idx], y[idx]),
            xytext=(ann.get('offset_x', 30), ann.get('offset_y', 30)),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', ec=colors['grid'], alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                          color=colors['primary'], lw=1.5),
            fontsize=9,
            color=colors['text']
        )

def create_no_stylized_plot(x_data, y_data, title="Nitric Oxide Dynamics", 
                           x_label="Time", y_label="Concentration",
                           highlight_regions=None):
    """Create a stylized plot with N1O1 branding"""
    colors = configure_mpl_style()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add subtle background pattern
    ax.set_facecolor('white')
    
    # Create main plot with gradient
    create_gradient_fill(ax, x_data, y_data, colors['no2'])
    
    # Highlight specific regions if provided
    if highlight_regions:
        for region in highlight_regions:
            ax.axvspan(region['start'], region['end'], 
                      alpha=0.2, color=region.get('color', colors['accent']),
                      label=region.get('label', ''))
    
    # Style the plot
    ax.set_xlabel(x_label, fontsize=12, fontweight='medium', color=colors['text'])
    ax.set_ylabel(y_label, fontsize=12, fontweight='medium', color=colors['text'])
    ax.set_title(title, fontsize=16, fontweight='bold', color=colors['primary'], pad=20)
    
    # Add subtle branding
    ax.text(0.99, 0.01, 'N1O1 Clinical Trials', transform=ax.transAxes,
            fontsize=8, color=colors['grid'], ha='right', va='bottom',
            alpha=0.7, style='italic')
    
    # Customize spines
    for spine in ax.spines.values():
        spine.set_color(colors['grid'])
        spine.set_linewidth(0.5)
    
    # Enhanced grid
    ax.grid(True, linestyle='-', alpha=0.3, color=colors['grid'])
    ax.set_axisbelow(True)
    
    # Tight layout
    plt.tight_layout()
    
    return fig, ax

def create_multi_panel_figure(data_dict, title="Comprehensive Nitric Oxide Analysis"):
    """Create a multi-panel figure for comprehensive data visualization"""
    colors = configure_mpl_style()
    
    n_panels = len(data_dict)
    fig, axes = plt.subplots(n_panels, 1, figsize=(12, 4*n_panels), sharex=True)
    
    if n_panels == 1:
        axes = [axes]
    
    for idx, (key, data) in enumerate(data_dict.items()):
        ax = axes[idx]
        
        # Plot with custom styling
        x = data['x']
        y = data['y']
        color = data.get('color', colors['no2'])
        label = data.get('label', key)
        
        # Create gradient fill
        create_gradient_fill(ax, x, y, color)
        
        # Labels
        ax.set_ylabel(label, fontsize=11, fontweight='medium')
        
        # Grid
        ax.grid(True, linestyle='-', alpha=0.3, color=colors['grid'])
        ax.set_axisbelow(True)
        
        # Customize spines
        for spine in ax.spines.values():
            spine.set_color(colors['grid'])
            spine.set_linewidth(0.5)
    
    # Common x-label
    axes[-1].set_xlabel('Time (minutes)', fontsize=12, fontweight='medium')
    
    # Main title
    fig.suptitle(title, fontsize=16, fontweight='bold', color=colors['primary'], y=0.98)
    
    # Add branding
    fig.text(0.99, 0.01, 'N1O1 Clinical Trials - Revolutionary NO Research', 
             fontsize=8, color=colors['grid'], ha='right', va='bottom',
             alpha=0.7, style='italic')
    
    plt.tight_layout()
    return fig, axes

def create_heatmap_visualization(data, title="Dose-Response Heatmap", 
                                cmap='RdBu_r', center=None):
    """Create publication-quality heatmap for dose-response data"""
    colors = configure_mpl_style()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    im = ax.imshow(data, cmap=cmap, aspect='auto', interpolation='bilinear')
    
    # Add colorbar with styling
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Response Magnitude', fontsize=11, fontweight='medium')
    cbar.ax.tick_params(labelsize=9)
    
    # Style
    ax.set_title(title, fontsize=14, fontweight='bold', color=colors['primary'], pad=15)
    
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add grid
    ax.grid(False)
    
    # Tight layout
    plt.tight_layout()
    
    return fig, ax

def add_significance_bars(ax, x1, x2, y, p_value, height_factor=0.05):
    """Add significance bars to plots"""
    colors = configure_mpl_style()
    
    # Get y-range for positioning
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    bar_height = y + height_factor * y_range
    
    # Draw the bar
    ax.plot([x1, x1, x2, x2], [y, bar_height, bar_height, y], 
            color=colors['primary'], linewidth=1.5)
    
    # Add significance stars
    if p_value < 0.001:
        sig_text = '***'
    elif p_value < 0.01:
        sig_text = '**'
    elif p_value < 0.05:
        sig_text = '*'
    else:
        sig_text = 'ns'
    
    ax.text((x1 + x2) / 2, bar_height + 0.01 * y_range, sig_text,
            ha='center', va='bottom', fontsize=10, fontweight='bold')
