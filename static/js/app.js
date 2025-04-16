/**
 * Main application JavaScript
 * Provides shared functionality across the application
 * Author: Dustin Salinas
 * License: MIT
 */

// Format a number with the specified precision
function formatNumber(number, precision = 2) {
    return parseFloat(number).toFixed(precision);
}

// Create a toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    // Create toast container if it doesn't exist
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Toast content
    const flexContainer = document.createElement('div');
    flexContainer.className = 'd-flex';
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    
    flexContainer.appendChild(toastBody);
    flexContainer.appendChild(closeButton);
    toastEl.appendChild(flexContainer);
    
    document.getElementById('toast-container').appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Remove toast after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function () {
        toastEl.remove();
    });
}

// Download data as a CSV file
function downloadCSV(data, filename = 'data.csv') {
    const csvContent = 'data:text/csv;charset=utf-8,' + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Download an image
function downloadImage(imageData, filename = 'plot.png') {
    const link = document.createElement('a');
    link.href = imageData;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Create a loader element
function createLoader(message = 'Loading...') {
    const loaderEl = document.createElement('div');
    loaderEl.className = 'text-center p-5';
    loaderEl.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">${message}</p>
    `;
    return loaderEl;
}

// Show loading indicator
function showLoading(containerId, message = 'Loading...') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
        container.appendChild(createLoader(message));
    }
}

// Hide loading indicator
function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        const loader = container.querySelector('.spinner-border')?.closest('.text-center');
        if (loader) {
            loader.remove();
        }
    }
}

// Fetch and display error
function handleFetchError(error, container) {
    console.error('Error:', error);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Error</h4>
                <p>${error.message || 'An unexpected error occurred'}</p>
            </div>
        `;
    }
}

// Format time for display
function formatTime(timeInMinutes) {
    if (timeInMinutes < 60) {
        return `${formatNumber(timeInMinutes, 1)} min`;
    } else {
        const hours = Math.floor(timeInMinutes / 60);
        const minutes = Math.round(timeInMinutes % 60);
        return `${hours}h ${minutes}m`;
    }
}

// Validate numeric input
function validateNumericInput(input, min, max) {
    const value = parseFloat(input.value);
    
    if (isNaN(value)) {
        input.value = input.dataset.lastValid || min;
        return false;
    }
    
    if (value < min) {
        input.value = min;
    } else if (value > max) {
        input.value = max;
    }
    
    input.dataset.lastValid = input.value;
    return true;
}

// Initialize numeric inputs
function initNumericInputs() {
    document.querySelectorAll('input[type="number"]').forEach(input => {
        const min = parseFloat(input.getAttribute('min') || '-Infinity');
        const max = parseFloat(input.getAttribute('max') || 'Infinity');
        
        input.dataset.lastValid = input.value;
        
        input.addEventListener('change', () => {
            validateNumericInput(input, min, max);
        });
        
        input.addEventListener('input', () => {
            validateNumericInput(input, min, max);
        });
    });
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(
        () => {
            showToast('Copied to clipboard!', 'success');
        },
        (err) => {
            showToast('Failed to copy: ' + err, 'danger');
        }
    );
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize toast container
    const toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize numeric inputs
    initNumericInputs();
});
