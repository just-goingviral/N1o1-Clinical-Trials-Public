
/**
 * Southern-style error message generator
 * Adds witty Southern charm to all error messages
 */

(function() {
    // Collection of Southern phrases to prepend to errors
    const southernPhrases = [
        "Well butter my biscuit!",
        "Bless your heart!",
        "Hold your horses, partner!",
        "Well I'll be!",
        "Sweet tea and cornbread!",
        "Heavens to Betsy!",
        "Lord have mercy!",
        "You're barkin' up the wrong tree!",
        "That dog won't hunt!",
        "Fixin' to have a conniption fit!",
        "Well slap my knee and call me Sally!"
    ];
    
    // Collection of Southern endings
    const southernEndings = [
        "Y'hear?",
        "Ain't that somethin'?",
        "Bless your heart.",
        "Mmhmm.",
        "That's just how the cookie crumbles 'round here.",
        "Fix it up right quick now.",
        "Ain't that just the cat's pajamas?",
        "Don't that beat all?",
        "We'll be back faster than greased lightning!",
        "We're on it like white on rice."
    ];
    
    // Convert standard error to Southern style
    window.convertToSouthernError = function(errorMsg) {
        const phrase = southernPhrases[Math.floor(Math.random() * southernPhrases.length)];
        const ending = southernEndings[Math.floor(Math.random() * southernEndings.length)];
        
        // Clean up the original message
        let cleanMsg = errorMsg.replace(/Error:|error:/gi, "").trim();
        cleanMsg = cleanMsg.charAt(0).toLowerCase() + cleanMsg.slice(1);
        
        // Build Southern style message
        return `${phrase} ${cleanMsg} ${ending}`;
    };
    
    // Find and convert all existing error messages on page load
    document.addEventListener('DOMContentLoaded', function() {
        try {
            // Target common error message containers
            const errorElements = document.querySelectorAll('.alert-danger, .error-message, [data-error-container]');
            
            errorElements.forEach(el => {
                if (el.textContent && el.textContent.trim() !== '') {
                    el.textContent = window.convertToSouthernError(el.textContent);
                }
            });
            
            // Add error listener to catch and style runtime errors
            window.addEventListener('error', function(event) {
                // Log to console
                console.error('Caught runtime error:', event.error);
                
                // Log to server if API is available
                if (window.fetch) {
                    fetch('/api/log-client-error', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            source: 'client_runtime',
                            error: event.error ? event.error.toString() : event.message,
                            context: window.location.href
                        })
                    }).catch(e => console.warn('Failed to log error:', e));
                }
                
                // Don't show alerts for every error - can flood the user
                // Instead, add a status indicator if it doesn't exist
                if (!document.getElementById('error-status-indicator')) {
                    const indicator = document.createElement('div');
                    indicator.id = 'error-status-indicator';
                    indicator.style.cssText = 'position:fixed;bottom:10px;left:10px;background:rgba(220,53,69,0.8);color:white;padding:5px 10px;border-radius:3px;font-size:12px;z-index:9999;';
                    indicator.innerHTML = window.convertToSouthernError('Errors detected');
                    document.body.appendChild(indicator);
                }
            });
        } catch (e) {
            console.error('Error initializing error handler:', e);
        }
    });
    
    // Override the default alert for errors - with resilient implementation
    try {
        const originalAlert = window.alert;
        window.alert = function(message) {
            try {
                if (message && (message.toString().toLowerCase().includes('error') || 
                               message.toString().toLowerCase().includes('fail'))) {
                    originalAlert(window.convertToSouthernError(message));
                    
                    // Also log to console for debugging
                    console.error('Error alert:', message);
                    
                    // Log to server if available
                    if (window.fetch) {
                        fetch('/api/log-client-error', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                source: 'alert',
                                error: message.toString(),
                                context: window.location.href
                            })
                        }).catch(e => console.warn('Failed to log error alert:', e));
                    }
                } else {
                    originalAlert(message);
                }
            } catch (e) {
                // Fallback to original alert if our customization fails
                console.error('Error in customized alert:', e);
                originalAlert(message);
                // Fallback to original alert if our customization fails
                console.error('Error in custom alert:', e);
                originalAlert(message);
            }
        };
    } catch (e) {
        console.error('Failed to override alert:', e);
    }
    
    // Global error handler for AJAX requests
    if (window.jQuery) {
        try {
            $(document).ajaxError(function(event, jqXHR, settings, thrownError) {
                console.error('AJAX error:', thrownError);
                
                // Log to server
                fetch('/api/log-client-error', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        source: 'ajax',
                        error: thrownError || jqXHR.statusText,
                        context: settings.url
                    })
                }).catch(e => console.warn('Failed to log AJAX error:', e));
            });
        } catch (e) {
            console.error('Failed to set up AJAX error handler:', e);
        }
    }
})();
