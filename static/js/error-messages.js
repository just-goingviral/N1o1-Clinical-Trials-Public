
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
        // Target common error message containers
        const errorElements = document.querySelectorAll('.alert-danger, .error-message, [data-error-container]');
        
        errorElements.forEach(el => {
            if (el.textContent && el.textContent.trim() !== '') {
                el.textContent = window.convertToSouthernError(el.textContent);
            }
        });
    });
    
    // Override the default alert for errors
    const originalAlert = window.alert;
    window.alert = function(message) {
        if (message.toLowerCase().includes('error') || message.toLowerCase().includes('fail')) {
            originalAlert(window.convertToSouthernError(message));
        } else {
            originalAlert(message);
        }
    };
})();
