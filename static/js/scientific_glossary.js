/**
 * N1O1 Clinical Trials - Scientific Terminology Glossary
 * A glossary of scientific terms related to nitric oxide research and clinical trials
 */

const SCIENTIFIC_TERMS = {
    // Nitric Oxide Basic Terminology
    "NO": {
        term: "Nitric Oxide (NO)",
        definition: "A gaseous signaling molecule produced naturally in the body that plays a crucial role in vasodilation, immune function, and neurotransmission.",
        category: "basic"
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
 */
function initScientificTooltips(container) {
    // Ensure Bootstrap tooltips are available
    if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) {
        console.error('Bootstrap tooltips not available. Ensure Bootstrap JS is loaded.');
        return;
    }
    
    const containerElement = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;
    
    if (!containerElement) {
        console.error('Container element not found:', container);
        return;
    }
    
    // Add tooltips to elements with data-scientific-term attributes
    const termElements = containerElement.querySelectorAll('[data-scientific-term]');
    
    termElements.forEach(element => {
        const term = element.getAttribute('data-scientific-term');
        const definition = getTermDefinition(term);
        
        if (definition) {
            element.setAttribute('data-bs-toggle', 'tooltip');
            element.setAttribute('data-bs-placement', 'top');
            element.setAttribute('title', definition.definition);
            
            // Add visual indicator and styling for tooltip terms
            element.classList.add('scientific-term');
            
            // Initialize Bootstrap tooltip
            new bootstrap.Tooltip(element);
        } else {
            console.warn(`Definition not found for scientific term: ${term}`);
        }
    });
}

/**
 * Scan text for scientific terms and add tooltips
 * @param {string|Element} container - CSS selector or DOM element to scan
 * @param {boolean} includeBasic - Whether to include basic terms (default: true)
 * @param {boolean} includeAdvanced - Whether to include advanced terms (default: true) 
 */
function scanForScientificTerms(container, includeBasic = true, includeAdvanced = true) {
    const containerElement = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;
    
    if (!containerElement) {
        console.error('Container element not found:', container);
        return;
    }
    
    // Create a temporary element to hold the content
    const tempElement = document.createElement('div');
    tempElement.innerHTML = containerElement.innerHTML;
    
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
        
        let text = currentNode.nodeValue;
        let newHtml = text;
        
        // Look for terms in the text
        for (const [key, value] of Object.entries(SCIENTIFIC_TERMS)) {
            // Skip terms based on category filter
            if ((value.category === 'basic' && !includeBasic) ||
                (value.category === 'advanced' && !includeAdvanced)) {
                continue;
            }
            
            // Regular expressions to find the term
            // We need to handle both exact terms and terms within words
            const exactRegExp = new RegExp(`\\b(${escapeRegExp(key)})\\b`, 'gi');
            
            // Replace exact matches with span elements
            newHtml = newHtml.replace(exactRegExp, (match) => {
                return `<span class="scientific-term" data-scientific-term="${key}">${match}</span>`;
            });
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
    }
    
    // Update the original container with the modified content
    containerElement.innerHTML = tempElement.innerHTML;
    
    // Initialize tooltips on the newly created elements
    initScientificTooltips(containerElement);
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