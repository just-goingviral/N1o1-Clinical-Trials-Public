/**
 * N1O1 Clinical Trials - Button Fix Utility
 * Repairs common button issues and ensures proper event handling
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Button fix utility running');
    
    // Fix tab navigation buttons
    fixTabButtons();
    
    // Fix stretched links
    fixStretchedLinks();
    
    // Fix dropdown menus
    fixDropdowns();
    
    // Add tooltips to scientific terms
    initializeScientificTerms();
    
    // Fix form submission buttons
    fixFormButtons();
    
    // Report status
    console.log('Button and interaction fixes applied');
});

/**
 * Fix tab navigation buttons that might not be working
 */
function fixTabButtons() {
    // Find all tab buttons
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    // Re-initialize tab functionality
    tabButtons.forEach(button => {
        // Clear existing event listeners by cloning
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add proper event listener
        newButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get target panel
            const targetId = this.getAttribute('data-bs-target');
            if (!targetId) return;
            
            // Hide all tab panes
            const tabPanes = document.querySelectorAll('.tab-pane');
            tabPanes.forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Show target pane
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
            
            // Update active state on buttons
            const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            });
            
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');
        });
    });
}

/**
 * Fix stretched links that might not be working properly
 */
function fixStretchedLinks() {
    // Find all cards with stretched links
    const stretchedLinks = document.querySelectorAll('.stretched-link');
    
    stretchedLinks.forEach(link => {
        // Find parent card
        const card = link.closest('.card');
        if (!card) return;
        
        // Add click event to the entire card
        card.style.cursor = 'pointer';
        card.addEventListener('click', function(event) {
            // Don't interfere with actual link clicks
            if (event.target.tagName === 'A') return;
            
            // Get the link's href
            const href = link.getAttribute('href');
            if (!href) return;
            
            // Navigate to the link target
            window.location.href = href;
        });
    });
}

/**
 * Fix dropdown menus that might not be working
 */
function fixDropdowns() {
    // Find all dropdown toggles
    const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    
    dropdownToggles.forEach(toggle => {
        // Create manual dropdown toggling
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            // Find dropdown menu
            const parent = this.closest('.dropdown');
            if (!parent) return;
            
            const menu = parent.querySelector('.dropdown-menu');
            if (!menu) return;
            
            // Toggle show class
            const isShown = menu.classList.contains('show');
            
            // Close all other dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                    openMenu.parentElement.classList.remove('show');
                }
            });
            
            // Toggle this dropdown
            if (isShown) {
                menu.classList.remove('show');
                parent.classList.remove('show');
            } else {
                menu.classList.add('show');
                parent.classList.add('show');
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
                menu.parentElement.classList.remove('show');
            });
        }
    });
}

/**
 * Fix form submission buttons
 */
function fixFormButtons() {
    // Find all forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Find submit buttons
        const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
        
        submitButtons.forEach(button => {
            // Ensure clicks lead to submission
            button.addEventListener('click', function(event) {
                // Check if the form is valid
                if (form.checkValidity()) {
                    console.log('Form submission triggered by button');
                } else {
                    // If not valid, prevent submission and show validation
                    event.preventDefault();
                    event.stopPropagation();
                    form.classList.add('was-validated');
                }
            });
        });
    });
}

/**
 * Add tooltip information to scientific terms
 */
function initializeScientificTerms() {
    // Define scientific term explanations
    const scientificTerms = {
        'NO₂⁻': 'Nitrite ion, which can be converted to nitric oxide in the body.',
        'NO': 'Nitric oxide, a crucial signaling molecule that helps blood vessels dilate.',
        'N1O1 Lozenge': 'A proprietary formulation designed to enhance nitric oxide production.',
        'nitric oxide': 'A molecule that plays key roles in cardiovascular health by regulating blood vessel dilation.',
        'bioavailability': 'The proportion of a substance that enters circulation when introduced into the body.',
        'PK': 'Pharmacokinetics - the study of how drugs move through the body.',
        'half-life': 'The time required for a substance to reduce to half its initial value in the body.',
        'compartmental model': 'A mathematical model that describes how substances move between different areas of the body.',
        'endothelium': 'The thin layer of cells that lines blood vessels and regulates exchanges between bloodstream and tissues.',
        'vasodilation': 'The widening of blood vessels resulting from relaxation of the vessel walls.',
        'hypoxia': 'A condition where tissues are deprived of adequate oxygen supply.',
        'cGMP': 'Cyclic guanosine monophosphate, a second messenger involved in vasodilation pathways.',
        'plasma nitrite': 'The concentration of nitrite in blood plasma, a biomarker for nitric oxide status.'
    };
    
    // Find all scientific terms
    const terms = document.querySelectorAll('[data-scientific-term]');
    
    terms.forEach(term => {
        const termName = term.getAttribute('data-scientific-term');
        const explanation = scientificTerms[termName] || 'Scientific term related to nitric oxide research.';
        
        // Add tooltip functionality
        term.setAttribute('title', explanation);
        term.classList.add('scientific-term');
        
        // Make the term interactive
        term.style.cursor = 'help';
        term.style.borderBottom = '1px dotted #3b7eb9';
        
        // Add click handler to show explanation for mobile users
        term.addEventListener('click', function(event) {
            // Prevent navigation if term is a link
            event.preventDefault();
            
            // Create and show tooltip manually for mobile
            const existingTooltip = document.getElementById('mobile-tooltip');
            if (existingTooltip) {
                existingTooltip.remove();
                return;
            }
            
            const tooltip = document.createElement('div');
            tooltip.id = 'mobile-tooltip';
            tooltip.className = 'mobile-scientific-tooltip';
            tooltip.innerHTML = `
                <div class="card bg-dark border-primary">
                    <div class="card-body p-2">
                        <h6 class="mb-1">${termName}</h6>
                        <p class="mb-0 small">${explanation}</p>
                    </div>
                </div>
            `;
            
            // Position near the term
            document.body.appendChild(tooltip);
            const rect = term.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
            tooltip.style.left = `${rect.left + window.scrollX}px`;
            tooltip.style.maxWidth = '300px';
            tooltip.style.zIndex = '1050';
            
            // Add click handler to remove
            document.addEventListener('click', function removeTooltip(e) {
                if (e.target !== term) {
                    tooltip.remove();
                    document.removeEventListener('click', removeTooltip);
                }
            });
        });
    });
}