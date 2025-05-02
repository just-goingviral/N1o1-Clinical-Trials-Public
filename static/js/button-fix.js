/**
 * Button functionality fix and enhancement script
 * Ensures all buttons have proper event handlers and accessibility
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Button fix script loaded');

    // Fix for buttons without event handlers
    function fixButtons() {
        const allButtons = document.querySelectorAll('button, .btn, [role="button"]');
        console.log(`Found ${allButtons.length} buttons to check`);

        allButtons.forEach((button, index) => {
            // Skip if disabled
            if (button.disabled || button.classList.contains('disabled')) {
                return;
            }

            // Add ID if missing (for tracking)
            if (!button.id) {
                button.id = `btn-${Date.now()}-${index}`;
            }

            // Ensure all buttons have proper ARIA attributes
            if (!button.getAttribute('aria-label') && button.innerText.trim()) {
                button.setAttribute('aria-label', button.innerText.trim());
            }

            // Add missing click handlers for buttons that should have them
            const needsHandler = !button.onclick && 
                                !button.hasAttribute('data-bs-toggle') &&
                                !button.hasAttribute('data-toggle') &&
                                !button.form &&
                                button.type !== 'submit' &&
                                button.type !== 'reset';

            if (needsHandler) {
                console.log(`Adding default handler to button: ${button.id}`);

                // If button has a data-action attribute, use it
                if (button.hasAttribute('data-action')) {
                    const action = button.getAttribute('data-action');
                    button.addEventListener('click', function(e) {
                        console.log(`Button action triggered: ${action}`);

                        // Handle known actions
                        if (action === 'back') {
                            window.history.back();
                        } else if (action.startsWith('navigate:')) {
                            const url = action.split(':')[1];
                            window.location.href = url;
                        }
                    });
                }
            }
        });
    }

    // Fix for form submissions
    function fixForms() {
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            // Check if form already has submit handler
            if (!form.onsubmit) {
                form.addEventListener('submit', function(e) {
                    // Prevent double submissions
                    const submitButtons = form.querySelectorAll('[type="submit"]');
                    submitButtons.forEach(button => {
                        button.disabled = true;
                        if (!button.getAttribute('data-original-text')) {
                            button.setAttribute('data-original-text', button.innerHTML);
                        }
                        button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;
                    });
                });
            }
        });
    }

    // Fix for AJAX buttons
    function fixAjaxButtons() {
        const ajaxButtons = document.querySelectorAll('[data-ajax="true"]');

        ajaxButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();

                const url = button.getAttribute('data-url');
                const method = button.getAttribute('data-method') || 'GET';
                const resultTarget = button.getAttribute('data-target');

                if (url) {
                    // Show loading state
                    button.disabled = true;
                    if (!button.getAttribute('data-original-text')) {
                        button.setAttribute('data-original-text', button.innerHTML);
                    }
                    button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`;

                    // Make the AJAX request
                    fetch(url, {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Update target element if specified
                        if (resultTarget) {
                            const targetEl = document.querySelector(resultTarget);
                            if (targetEl) {
                                if (typeof data === 'object') {
                                    targetEl.textContent = JSON.stringify(data);
                                } else {
                                    targetEl.textContent = data;
                                }
                            }
                        }

                        // Show success state briefly
                        button.innerHTML = `<i class="bi bi-check-circle"></i> Success`;
                        setTimeout(() => {
                            button.innerHTML = button.getAttribute('data-original-text');
                            button.disabled = false;
                        }, 2000);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        button.innerHTML = `<i class="bi bi-exclamation-triangle"></i> Error`;
                        setTimeout(() => {
                            button.innerHTML = button.getAttribute('data-original-text');
                            button.disabled = false;
                        }, 2000);
                    });
                }
            });
        });
    }

    // Fix for modal buttons
    function fixModalButtons() {
        // Ensure modals can be opened and closed
        const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"], [data-toggle="modal"]');

        modalTriggers.forEach(trigger => {
            // Add click handler if not using Bootstrap's data attributes properly
            trigger.addEventListener('click', function(e) {
                const targetSelector = trigger.getAttribute('data-bs-target') || trigger.getAttribute('data-target');
                if (!targetSelector) return;

                const modal = document.querySelector(targetSelector);
                if (!modal) return;

                // Try using Bootstrap 5 method first
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                } 
                // Fallback to Bootstrap 4
                else if (typeof jQuery !== 'undefined' && jQuery.fn.modal) {
                    jQuery(modal).modal('show');
                }
                // Manual fallback if Bootstrap is not available
                else {
                    modal.style.display = 'block';
                    modal.classList.add('show');
                    document.body.classList.add('modal-open');
                }
            });
        });
    }

    // Run all fixes
    fixButtons();
    fixForms();
    fixAjaxButtons();
    fixModalButtons();

    // Run fixes again when DOM changes (for dynamically added buttons)
    const observer = new MutationObserver(function(mutations) {
        fixButtons();
        fixForms();
        fixAjaxButtons();
        fixModalButtons();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('Button fix script completed');
});