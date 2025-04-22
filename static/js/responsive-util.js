
/**
 * N1O1 Responsive Utilities
 * Provides responsive behavior and adaptations for different screen sizes
 */

// Initialize responsive elements when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize responsive elements
    initResponsiveElements();
    
    // Handle window resize
    window.addEventListener('resize', debounce(function() {
        handleResponsiveChanges();
    }, 250));
    
    // Initial call to handle responsive behavior
    handleResponsiveChanges();
    
    // Initialize back-to-top button
    initBackToTopButton();
});

// Initialize responsive elements
function initResponsiveElements() {
    // Add touch-friendly behavior to buttons
    const touchButtons = document.querySelectorAll('.btn, .card, .nav-link');
    touchButtons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        button.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        });
    });
    
    // Make tables responsive if not already
    const tables = document.querySelectorAll('table:not(.table-responsive)');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Handle responsive changes based on screen size
function handleResponsiveChanges() {
    const width = window.innerWidth;
    
    // Mobile adjustments (screens smaller than 768px)
    if (width < 768) {
        // Replace long button text with icons on small screens
        const buttonTexts = document.querySelectorAll('.btn-icon-only-xs .btn-text');
        buttonTexts.forEach(text => {
            text.style.display = 'none';
        });
        
        // Adjust chart height for better mobile viewing
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            container.style.height = '300px';
        });
        
        // Show mobile navigation if available
        const mobileNav = document.getElementById('mobile-nav');
        if (mobileNav) {
            mobileNav.style.display = 'flex';
        }
        
        // Apply mobile-friendly styling to forms
        const formControls = document.querySelectorAll('.form-control, .form-select, .btn');
        formControls.forEach(control => {
            control.style.minHeight = '44px'; // Better touch targets
        });
    } else {
        // Desktop adjustments
        // Restore button text on larger screens
        const buttonTexts = document.querySelectorAll('.btn-icon-only-xs .btn-text');
        buttonTexts.forEach(text => {
            text.style.display = 'inline';
        });
        
        // Restore chart height on larger screens
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            container.style.height = '400px';
        });
        
        // Hide mobile navigation on larger screens
        const mobileNav = document.getElementById('mobile-nav');
        if (mobileNav) {
            mobileNav.style.display = 'none';
        }
        
        // Reset form control heights
        const formControls = document.querySelectorAll('.form-control, .form-select, .btn');
        formControls.forEach(control => {
            control.style.minHeight = '';
        });
    }
}

// Initialize back-to-top button
function initBackToTopButton() {
    // Create back-to-top button if it doesn't exist
    if (!document.getElementById('back-to-top-btn')) {
        const backToTopBtn = document.createElement('button');
        backToTopBtn.id = 'back-to-top-btn';
        backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTopBtn.setAttribute('aria-label', 'Back to top');
        backToTopBtn.setAttribute('title', 'Back to top');
        document.body.appendChild(backToTopBtn);
        
        // Show button when user scrolls down
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'flex';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        // Scroll to top when clicked
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Utility function to debounce events
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}

// Export utility functions
window.N1O1Responsive = {
    refresh: handleResponsiveChanges,
    init: initResponsiveElements
};
