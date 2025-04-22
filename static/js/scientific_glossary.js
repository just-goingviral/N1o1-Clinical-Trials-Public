/**
 * N1O1 Clinical Trials - Scientific Terminology Glossary
 * A glossary of scientific terms related to nitric oxide research and clinical trials
 */

// Scientific glossary with enhanced visualization
const SCIENTIFIC_TERMS = {
    // Nitric Oxide Basic Terminology
    "NO": {
        term: "Nitric Oxide (NO)",
        definition: "A gaseous signaling molecule produced naturally in the body that plays a crucial role in vasodilation, immune function, and neurotransmission.",
        category: "basic",
        icon: "🧪",
        color: "#3b7eb9"
    },
    "NO₂⁻": {
        term: "Nitrite (NO₂⁻)",
        definition: "An ionic form of nitrogen oxide that serves as a storage pool for nitric oxide in the body. Dietary nitrites can be converted to NO in the body under certain conditions.",
        category: "basic"
    },
    "NO₃⁻": {
        term: "Nitrate (NO₃⁻)",
        definition: "An ionic compound that is present in many foods and can be converted to nitrite and eventually to nitric oxide in the body.",
        category: "basic"
    },
    "cGMP": {
        term: "Cyclic Guanosine Monophosphate (cGMP)",
        definition: "A secondary messenger molecule that mediates many of the effects of nitric oxide, particularly in smooth muscle relaxation and vasodilation.",
        category: "advanced"
    },
    "GC": {
        term: "Guanylyl Cyclase (GC)",
        definition: "An enzyme that is activated by nitric oxide and catalyzes the conversion of guanosine triphosphate (GTP) to cyclic guanosine monophosphate (cGMP).",
        category: "advanced"
    },

    // Physiological Terms
    "vasodilation": {
        term: "Vasodilation",
        definition: "The widening of blood vessels due to relaxation of smooth muscle cells, often mediated by nitric oxide, resulting in increased blood flow and decreased blood pressure.",
        category: "basic"
    },
    "endothelium": {
        term: "Endothelium",
        definition: "The inner lining of blood vessels that produces nitric oxide to regulate vascular tone, blood pressure, and other cardiovascular functions.",
        category: "basic"
    },
    "hypoxia": {
        term: "Hypoxia",
        definition: "A condition of low oxygen levels in tissues, which can activate nitrite conversion to nitric oxide as a compensatory mechanism to increase blood flow.",
        category: "basic"
    },
    "eNOS": {
        term: "Endothelial Nitric Oxide Synthase (eNOS)",
        definition: "An enzyme expressed in endothelial cells that catalyzes the production of nitric oxide from L-arginine in the presence of oxygen.",
        category: "advanced"
    },

    // Measurement and Clinical Terms
    "plasma nitrite": {
        term: "Plasma Nitrite",
        definition: "The concentration of nitrite (NO₂⁻) in blood plasma, often measured as a biomarker of nitric oxide status and vascular health.",
        category: "basic"
    },
    "bioavailability": {
        term: "Bioavailability",
        definition: "The proportion of a substance that enters circulation when introduced into the body and is able to have an active effect.",
        category: "basic"
    },
    "half-life": {
        term: "Half-Life",
        definition: "The time required for a substance's concentration to decrease to half its initial value, indicating how quickly it is metabolized or eliminated from the body.",
        category: "basic"
    },
    "PK": {
        term: "Pharmacokinetics (PK)",
        definition: "The study of how a drug is absorbed, distributed, metabolized, and excreted by the body over time.",
        category: "advanced"
    },

    // Simulation and Analysis Terms
    "compartmental model": {
        term: "Compartmental Model",
        definition: "A mathematical model used to describe the way substances distribute and move between different compartments (e.g., blood, tissues) in the body.",
        category: "advanced"
    },
    "AUC": {
        term: "Area Under the Curve (AUC)",
        definition: "A measure of total exposure to a substance over time, calculated as the area under the concentration-time curve in pharmacokinetic analysis.",
        category: "advanced"
    },
    "Cmax": {
        term: "Maximum Concentration (Cmax)",
        definition: "The highest plasma concentration of a substance observed after administration, typically used in pharmacokinetic analysis.",
        category: "advanced"
    },
    "Tmax": {
        term: "Time to Maximum Concentration (Tmax)",
        definition: "The time at which the maximum plasma concentration of a substance is observed after administration.",
        category: "advanced"
    },

    // N1O1 Specific Terms
    "N1O1 Lozenge": {
        term: "N1O1 Lozenge",
        definition: "A proprietary nitric oxide-generating lozenge designed to enhance NO bioavailability through oral delivery of nitrite and complementary compounds.",
        category: "product"
    }
};

/**
 * Get a definition for a scientific term
 * @param {string} term - The term to look up
 * @returns {object|null} - The term definition object or null if not found
 */
function getTermDefinition(term) {
    const normalizedTerm = term.toLowerCase().trim();

    // Try direct match first
    if (SCIENTIFIC_TERMS[normalizedTerm]) {
        return SCIENTIFIC_TERMS[normalizedTerm];
    }

    // Try alternate forms
    for (const [key, value] of Object.entries(SCIENTIFIC_TERMS)) {
        if (normalizedTerm === key.toLowerCase() || 
            normalizedTerm === value.term.toLowerCase()) {
            return value;
        }
    }

    // Check if term is part of any keys or definitions
    for (const [key, value] of Object.entries(SCIENTIFIC_TERMS)) {
        if (key.toLowerCase().includes(normalizedTerm) || 
            value.term.toLowerCase().includes(normalizedTerm)) {
            return value;
        }
    }

    return null;
}

/**
 * Initialize tooltips for scientific terms in a container element
 * @param {string|Element} container - CSS selector or DOM element to scan for terms
 * @param {Object} options - Optional configuration settings
 * @param {string} options.placement - Tooltip placement (top, bottom, left, right)
 * @param {boolean} options.allowHtml - Whether to allow HTML in tooltips
 * @param {number} options.delay - Delay in ms before showing tooltip

// Initialize enhanced scientific tooltip functionality
function initEnhancedScientificTooltips() {
    // Find all elements with data-scientific-term attribute
    const scientificTerms = document.querySelectorAll('[data-scientific-term]');
    
    scientificTerms.forEach(element => {
        // Get the term key
        const termKey = element.getAttribute('data-scientific-term');
        
        // If term exists in our glossary
        if (SCIENTIFIC_TERMS[termKey]) {
            const termInfo = SCIENTIFIC_TERMS[termKey];
            
            // Add visual indicator
            const icon = termInfo.icon || '🔬';
            const color = termInfo.color || '#2063c9';
            
            // Add styling to the element
            element.style.borderBottom = `2px dotted ${color}`;
            element.style.position = 'relative';
            element.style.cursor = 'help';
            element.style.transition = 'background-color 0.2s ease';
            
            // Add hover effect
            element.addEventListener('mouseenter', function() {
                this.style.backgroundColor = `${color}22`; // Add slight background with transparency
            });
            
            element.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'transparent';
            });
            
            // Create tooltip content
            const tooltipContent = `
                <div style="font-weight: bold; margin-bottom: 4px;">${icon} ${termInfo.term}</div>
                <div>${termInfo.definition}</div>
                ${termInfo.category ? `<div style="margin-top: 5px; font-size: 0.8em; opacity: 0.7;">Category: ${termInfo.category}</div>` : ''}
            `;
            
            // Initialize tooltip using Bootstrap if available, or create custom implementation
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                new bootstrap.Tooltip(element, {
                    title: tooltipContent,
                    html: true,
                    placement: 'top',
                    trigger: 'hover focus',
                    container: 'body'
                });
            } else {
                // Custom tooltip implementation if Bootstrap is not available
                element.setAttribute('title', termInfo.definition);
            }
        }
    });
    
    console.log('Enhanced scientific terminology tooltips initialized');
}

// Export functions
window.N1O1Glossary = {
    terms: SCIENTIFIC_TERMS,
    initTooltips: initEnhancedScientificTooltips
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    if (typeof bootstrap !== 'undefined') {
        initEnhancedScientificTooltips();
    }
});

 */
function initScientificTooltips(container, options = {}) {
    // Set default options
    const defaultOptions = {
        placement: 'top',
        allowHtml: false,
        delay: 100
    };

    const tooltipOptions = { ...defaultOptions, ...options };

    // Ensure Bootstrap tooltips are available
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap is not available. Ensure Bootstrap JS is loaded.');
        // Try to load Bootstrap if it might be available later
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined') {
                console.log('Bootstrap now available, initializing tooltips...');
                initScientificTooltips(container, options);
            }
        }, 1000);
        return;
    }

    if (!bootstrap.Tooltip) {
        console.error('Bootstrap tooltips not available.');
        return;
    }

    const containerElements = [];

    if (typeof container === 'string') {
        // If a string selector is provided, query all matching elements
        const elements = document.querySelectorAll(container);
        if (elements.length === 0) {
            console.warn(`No elements found matching selector: ${container}`);
        } else {
            elements.forEach(el => containerElements.push(el));
        }
    } else if (container instanceof Element) {
        containerElements.push(container);
    } else if (container instanceof NodeList || Array.isArray(container)) {
        container.forEach(el => {
            if (el instanceof Element) {
                containerElements.push(el);
            }
        });
    } else if (!container) {
        // If no container is provided, use the entire document body
        containerElements.push(document.body);
    } else {
        console.error('Invalid container provided:', container);
        return;
    }

    if (containerElements.length === 0) {
        console.warn('No valid container elements found');
        return;
    }

    // Process each container element
    containerElements.forEach(containerElement => {
        try {
            // Add tooltips to elements with data-scientific-term attributes
            const termElements = containerElement.querySelectorAll('[data-scientific-term]');

            if (termElements.length === 0) {
                console.debug(`No scientific terms found in container: ${containerElement.tagName || 'unknown'}`);
            }

            termElements.forEach(element => {
                try {
                    // Clean up any existing tooltips on this element
                    if (element._tooltipInstance) {
                        element._tooltipInstance.dispose();
                    }

                    const term = element.getAttribute('data-scientific-term');
                    const definition = getTermDefinition(term);

                    if (definition) {
                        // Add category as data attribute for styling
                        if (definition.category) {
                            element.setAttribute('data-category', definition.category);
                        }

                        // Set up tooltip attributes
                        element.setAttribute('data-bs-toggle', 'tooltip');
                        element.setAttribute('data-bs-placement', tooltipOptions.placement);
                        element.setAttribute('data-bs-html', tooltipOptions.allowHtml ? 'true' : 'false');
                        element.setAttribute('title', definition.definition);

                        // Add visual indicator and styling for tooltip terms
                        element.classList.add('scientific-term');

                        // Initialize Bootstrap tooltip with options
                        const tooltip = new bootstrap.Tooltip(element, {
                            placement: tooltipOptions.placement,
                            html: tooltipOptions.allowHtml,
                            delay: {
                                show: tooltipOptions.delay,
                                hide: 50
                            },
                            trigger: 'hover focus',
                            container: 'body'
                        });

                        // Store reference to tooltip instance for potential cleanup
                        element._tooltipInstance = tooltip;
                    } else {
                        console.warn(`Definition not found for scientific term: ${term}`);
                        // Still add styling to indicate it's a scientific term
                        element.classList.add('scientific-term');
                        element.classList.add('undefined-term');

                        // Add a generic tooltip to indicate it's a scientific term
                        element.setAttribute('data-bs-toggle', 'tooltip');
                        element.setAttribute('data-bs-placement', tooltipOptions.placement);
                        element.setAttribute('title', 'Scientific term');

                        new bootstrap.Tooltip(element);
                    }
                } catch (elementError) {
                    console.error('Error processing scientific term element:', elementError);
                }
            });
        } catch (containerError) {
            console.error('Error processing container element:', containerError);
        }
    });
}

/**
 * Scan text for scientific terms and add tooltips
 * @param {string|Element} container - CSS selector or DOM element to scan
 * @param {Object} options - Optional configuration settings
 * @param {boolean} options.includeBasic - Whether to include basic terms (default: true)
 * @param {boolean} options.includeAdvanced - Whether to include advanced terms (default: true)
 * @param {boolean} options.includeProduct - Whether to include product terms (default: true)
 * @param {boolean} options.preserveExisting - Don't modify elements that already have tooltips (default: true)
 * @param {string[]} options.onlyTerms - Limit scanning to only these terms (optional)
 * @param {string[]} options.excludeTerms - Exclude these terms from scanning (optional)
 * @param {boolean} options.limitReplacement - Limit to one occurrence per term (default: false)
 */
function scanForScientificTerms(container, options = {}) {
    // Default options
    const defaultOptions = {
        includeBasic: true,
        includeAdvanced: true,
        includeProduct: true,
        preserveExisting: true,
        onlyTerms: null,
        excludeTerms: null,
        limitReplacement: false
    };

    // Merge with provided options
    const scanOptions = { ...defaultOptions, ...options };

    // Handle backward compatibility
    if (typeof arguments[1] === 'boolean') {
        scanOptions.includeBasic = arguments[1];
    }
    if (typeof arguments[2] === 'boolean') {
        scanOptions.includeAdvanced = arguments[2];
    }

    // Handle multiple containers
    const containerElements = [];

    try {
        if (typeof container === 'string') {
            const elements = document.querySelectorAll(container);
            if (elements.length === 0) {
                console.warn(`No elements found matching selector: ${container}`);
                return;
            }
            elements.forEach(el => containerElements.push(el));
        } else if (container instanceof Element) {
            containerElements.push(container);
        } else if (container instanceof NodeList || Array.isArray(container)) {
            container.forEach(el => {
                if (el instanceof Element) {
                    containerElements.push(el);
                }
            });
        } else if (!container) {
            // If no container is provided, use document body
            containerElements.push(document.body);
        } else {
            console.error('Invalid container provided:', container);
            return;
        }

        if (containerElements.length === 0) {
            console.warn('No valid container elements found');
            return;
        }

        // Process each container element
        containerElements.forEach(containerElement => processSingleContainer(containerElement, scanOptions));
    } catch (error) {
        console.error('Error in scanForScientificTerms:', error);
    }
}

/**
 * Process a single container element to find and replace scientific terms
 * @param {Element} containerElement - DOM element to scan
 * @param {Object} options - Scanning options
 * @private
 */
function processSingleContainer(containerElement, options) {
    try {
        // Create a temporary element to hold the content
        const tempElement = document.createElement('div');
        tempElement.innerHTML = containerElement.innerHTML;

        // Keep track of which terms we've already replaced if limiting replacements
        const replacedTerms = new Set();

        // Process all text nodes in the container
        const walker = document.createTreeWalker(
            tempElement,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const nodesToReplace = [];
        let currentNode;

        while (currentNode = walker.nextNode()) {
            // Skip nodes that are in scripts, styles, or already in tooltips
            if (isInUnwantedElement(currentNode)) {
                continue;
            }

            // Skip empty or whitespace-only nodes
            if (!currentNode.nodeValue.trim()) {
                continue;
            }

            let text = currentNode.nodeValue;
            let newHtml = text;

            // Look for terms in the text
            for (const [key, value] of Object.entries(SCIENTIFIC_TERMS)) {
                // Skip if we're limiting replacements and this term was already replaced
                if (options.limitReplacement && replacedTerms.has(key)) {
                    continue;
                }

                // Skip terms based on category filter
                if ((value.category === 'basic' && !options.includeBasic) ||
                    (value.category === 'advanced' && !options.includeAdvanced) ||
                    (value.category === 'product' && !options.includeProduct)) {
                    continue;
                }

                // Skip if not in onlyTerms (if specified)
                if (options.onlyTerms && Array.isArray(options.onlyTerms) && 
                    !options.onlyTerms.includes(key)) {
                    continue;
                }

                // Skip if in excludeTerms
                if (options.excludeTerms && Array.isArray(options.excludeTerms) && 
                    options.excludeTerms.includes(key)) {
                    continue;
                }

                // Regular expressions to find the term
                // We need to handle both exact terms and terms within words
                const exactRegExp = new RegExp(`\\b(${escapeRegExp(key)})\\b`, 'gi');

                // Replace exact matches with span elements
                let replaced = false;
                newHtml = newHtml.replace(exactRegExp, (match) => {
                    replaced = true;
                    return `<span class="scientific-term" data-scientific-term="${key}" data-category="${value.category}">${match}</span>`;
                });

                // If we replaced and we're limiting, add to replacedTerms
                if (replaced && options.limitReplacement) {
                    replacedTerms.add(key);
                }
            }

            // If modifications were made, queue the node for replacement
            if (newHtml !== text) {
                nodesToReplace.push({
                    node: currentNode,
                    newHtml: newHtml
                });
            }
        }

        // Replace nodes with modified ones
        for (const {node, newHtml} of nodesToReplace) {
            try {
                const replacementNode = document.createElement('span');
                replacementNode.innerHTML = newHtml;

                // Replace the old node with the new content
                if (node.parentNode) {
                    // We need to add all the children of the replacement node
                    const fragment = document.createDocumentFragment();
                    while (replacementNode.firstChild) {
                        fragment.appendChild(replacementNode.firstChild);
                    }

                    node.parentNode.replaceChild(fragment, node);
                }
            } catch (replaceError) {
                console.error('Error replacing node:', replaceError);
            }
        }

        // Only apply changes if nodes were actually replaced
        if (nodesToReplace.length > 0) {
            try {
                // Update the original container with the modified content
                // Carefully preserve any event listeners by only updating innerHTML if needed
                if (containerElement.innerHTML !== tempElement.innerHTML) {
                    containerElement.innerHTML = tempElement.innerHTML;
                }

                // Initialize tooltips on the newly created elements with enhanced options
                initScientificTooltips(containerElement, {
                    placement: 'auto',
                    allowHtml: true,
                    delay: 200
                });

                console.debug(`Processed ${nodesToReplace.length} text nodes with scientific terms in container`);
            } catch (updateError) {
                console.error('Error updating container HTML:', updateError);
            }
        }
    } catch (containerError) {
        console.error('Error processing container:', containerError);
    }
}

/**
 * Check if a text node is within an unwanted element
 * @param {Node} node - The text node to check
 * @returns {boolean} - True if the node is in an unwanted element
 */
function isInUnwantedElement(node) {
    let parent = node.parentNode;

    while (parent) {
        const tagName = parent.tagName?.toLowerCase();

        if (['script', 'style', 'noscript', 'code', 'pre'].includes(tagName)) {
            return true;
        }

        // Skip if already in a tooltip
        if (parent.hasAttribute && 
            (parent.hasAttribute('data-bs-toggle') || 
             parent.classList.contains('scientific-term'))) {
            return true;
        }

        parent = parent.parentNode;
    }

    return false;
}

/**
 * Escape special characters in a string for use in a regular expression
 * @param {string} string - The string to escape
 * @returns {string} - The escaped string
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Export functions for use in other scripts
window.N1O1Glossary = {
    getTermDefinition,
    initScientificTooltips,
    scanForScientificTerms,
    SCIENTIFIC_TERMS
};