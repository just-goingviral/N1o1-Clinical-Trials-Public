
/**
 * Responsive Utility Module for N1O1 Clinical Trials
 * Handles responsive design adjustments and media query helpers
 */

const ResponsiveUtil = (function() {
    // Device breakpoints
    const breakpoints = {
        xs: 0,
        sm: 576,
        md: 768,
        lg: 992,
        xl: 1200,
        xxl: 1400
    };
    
    /**
     * Check if the current viewport matches a breakpoint range
     * @param {string} size - Size name (xs, sm, md, lg, xl, xxl)
     * @returns {boolean} - Whether the current viewport matches the size
     */
    function isBreakpoint(size) {
        const width = window.innerWidth;
        
        switch(size) {
            case 'xs': return width < breakpoints.sm;
            case 'sm': return width >= breakpoints.sm && width < breakpoints.md;
            case 'md': return width >= breakpoints.md && width < breakpoints.lg;
            case 'lg': return width >= breakpoints.lg && width < breakpoints.xl;
            case 'xl': return width >= breakpoints.xl && width < breakpoints.xxl;
            case 'xxl': return width >= breakpoints.xxl;
            default: return false;
        }
    }
    
    /**
     * Check if the current viewport is at least a certain size
     * @param {string} size - Minimum size (sm, md, lg, xl, xxl)
     * @returns {boolean} - Whether the current viewport is at least the specified size
     */
    function isAtLeast(size) {
        const width = window.innerWidth;
        const sizeValue = breakpoints[size] || 0;
        return width >= sizeValue;
    }
    
    /**
     * Apply responsive adjustments based on current viewport size
     * @param {Object} element - DOM element to adjust
     * @param {Object} options - Adjustment options by breakpoint
     */
    function applyResponsiveStyles(element, options) {
        if (!element) return;
        
        // Reset existing responsive styles
        const responsiveClassesToRemove = Array.from(element.classList)
            .filter(cls => cls.startsWith('responsive-'));
        
        element.classList.remove(...responsiveClassesToRemove);
        
        // Apply new styles based on current breakpoint
        Object.keys(breakpoints).forEach(size => {
            if (isBreakpoint(size) && options[size]) {
                // Apply classes
                if (options[size].classes) {
                    element.classList.add(...options[size].classes);
                }
                
                // Apply inline styles
                if (options[size].styles) {
                    Object.assign(element.style, options[size].styles);
                }
                
                // Apply attributes
                if (options[size].attributes) {
                    Object.entries(options[size].attributes).forEach(([attr, value]) => {
                        element.setAttribute(attr, value);
                    });
                }
                
                // Add marker class
                element.classList.add(`responsive-${size}`);
            }
        });
    }
    
    /**
     * Initialize responsive listeners for dynamic adjustments
     * @param {function} callback - Function to call when viewport size changes
     * @returns {function} - Function to remove the listener
     */
    function initResponsiveListener(callback) {
        if (typeof callback !== 'function') return () => {};
        
        const handler = () => {
            callback();
        };
        
        // Set initial state
        handler();
        
        // Add resize listener
        window.addEventListener('resize', handler);
        
        // Return cleanup function
        return () => {
            window.removeEventListener('resize', handler);
        };
    }
    
    // Adjust chat interface elements for mobile
    function adjustChatInterface() {
        const chatButton = document.getElementById('no-molecule-chat-button');
        const chatContainer = document.getElementById('no-molecule-chat-container');
        
        if (!chatButton || !chatContainer) return;
        
        if (isBreakpoint('xs') || isBreakpoint('sm')) {
            // Mobile adjustments
            chatContainer.classList.add('mobile-chat');
            chatButton.classList.add('mobile-button');
        } else {
            // Desktop adjustments
            chatContainer.classList.remove('mobile-chat');
            chatButton.classList.remove('mobile-button');
        }
    }
    
    // Public API
    return {
        isBreakpoint,
        isAtLeast,
        applyResponsiveStyles,
        initResponsiveListener,
        adjustChatInterface,
        breakpoints
    };
})();

// Initialize responsive adjustments when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up responsive listener for the chat interface
    ResponsiveUtil.initResponsiveListener(() => {
        ResponsiveUtil.adjustChatInterface();
    });
    
    // Apply any other responsive adjustments
    const resizeElements = document.querySelectorAll('[data-responsive]');
    
    resizeElements.forEach(element => {
        try {
            const options = JSON.parse(element.dataset.responsive || '{}');
            ResponsiveUtil.applyResponsiveStyles(element, options);
        } catch (e) {
            console.error('Error parsing responsive options:', e);
        }
    });
});

// Make available globally
window.ResponsiveUtil = ResponsiveUtil;
