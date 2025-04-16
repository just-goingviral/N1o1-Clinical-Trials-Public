/**
 * Chart.js configuration
 * Provides consistent chart styling and options
 * Author: Dustin Salinas
 * License: MIT
 */

// Set default Chart.js options
Chart.defaults.color = '#e9ecef';
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.font.size = 12;
Chart.defaults.elements.line.borderWidth = 2;
Chart.defaults.elements.line.tension = 0.4;
Chart.defaults.elements.point.radius = 0;
Chart.defaults.elements.point.hoverRadius = 5;
Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.plugins.title.font.size = 16;
Chart.defaults.plugins.title.font.weight = 'bold';
Chart.defaults.plugins.legend.labels.usePointStyle = true;

// Color schemes
const colorSchemes = {
    primary: [
        'rgba(128, 0, 128, 1)',    // Purple (NO2-)
        'rgba(0, 128, 0, 1)',      // Green (cGMP) 
        'rgba(0, 123, 255, 1)'     // Blue (Vasodilation)
    ],
    secondary: [
        'rgba(220, 53, 69, 1)',    // Red
        'rgba(255, 193, 7, 1)',    // Yellow
        'rgba(23, 162, 184, 1)'    // Teal
    ],
    comparison: [
        'rgba(128, 0, 128, 1)',    // Purple
        'rgba(220, 53, 69, 1)',    // Red
        'rgba(255, 193, 7, 1)',    // Yellow
        'rgba(23, 162, 184, 1)',   // Teal
        'rgba(0, 128, 0, 1)',      // Green
        'rgba(0, 123, 255, 1)',    // Blue
        'rgba(108, 117, 125, 1)',  // Gray
        'rgba(255, 127, 80, 1)'    // Coral
    ]
};

// Chart background colors with transparency
function getBackgroundColor(color, alpha = 0.1) {
    return color.replace(/[^,]+(?=\))/, alpha);
}

// Create NO dynamics line chart configuration
function createNODynamicsChartConfig(data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time (minutes)'
                },
                ticks: {
                    maxTicksLimit: 10
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Concentration'
                },
                min: 0
            },
            y1: {
                position: 'right',
                title: {
                    display: true,
                    text: 'Vasodilation (%)'
                },
                min: 95,
                grid: {
                    drawOnChartArea: false
                }
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += context.parsed.y.toFixed(2);
                        return label;
                    }
                }
            }
        }
    };
    
    // Merge options
    const mergedOptions = {...defaultOptions, ...options};
    
    // Create datasets
    const datasets = [
        {
            label: 'Plasma NO₂⁻ (µM)',
            data: data.no2,
            borderColor: colorSchemes.primary[0],
            backgroundColor: getBackgroundColor(colorSchemes.primary[0]),
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.4
        },
        {
            label: 'cGMP (a.u.)',
            data: data.cgmp,
            borderColor: colorSchemes.primary[1],
            backgroundColor: getBackgroundColor(colorSchemes.primary[1]),
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            tension: 0.4
        },
        {
            label: 'Vasodilation (%)',
            data: data.vasodilation,
            borderColor: colorSchemes.primary[2],
            backgroundColor: getBackgroundColor(colorSchemes.primary[2]),
            borderWidth: 2,
            borderDash: [2, 2],
            pointRadius: 0,
            tension: 0.4,
            yAxisID: 'y1'
        }
    ];
    
    return {
        type: 'line',
        data: {
            labels: data.time,
            datasets: datasets
        },
        options: mergedOptions
    };
}

// Create comparison chart configuration
function createComparisonChartConfig(data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time (minutes)'
                },
                ticks: {
                    maxTicksLimit: 10
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Concentration (µM)'
                },
                min: 0
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += context.parsed.y.toFixed(2);
                        return label;
                    }
                }
            }
        }
    };
    
    // Merge options
    const mergedOptions = {...defaultOptions, ...options};
    
    // Create datasets
    const datasets = data.datasets.map((dataset, index) => {
        return {
            label: dataset.label,
            data: dataset.data,
            borderColor: colorSchemes.comparison[index % colorSchemes.comparison.length],
            backgroundColor: getBackgroundColor(colorSchemes.comparison[index % colorSchemes.comparison.length]),
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.4
        };
    });
    
    return {
        type: 'line',
        data: {
            labels: data.time,
            datasets: datasets
        },
        options: mergedOptions
    };
}

// Create bar chart configuration
function createBarChartConfig(data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
    
    // Merge options
    const mergedOptions = {...defaultOptions, ...options};
    
    return {
        type: 'bar',
        data: data,
        options: mergedOptions
    };
}

// Create scatter plot configuration
function createScatterChartConfig(data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: {
                    display: true,
                    text: options.xLabel || 'X'
                }
            },
            y: {
                title: {
                    display: true,
                    text: options.yLabel || 'Y'
                }
            }
        }
    };
    
    // Merge options
    const mergedOptions = {...defaultOptions, ...options};
    
    return {
        type: 'scatter',
        data: data,
        options: mergedOptions
    };
}
