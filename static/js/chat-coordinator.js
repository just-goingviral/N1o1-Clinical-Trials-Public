/**
 * Chat Coordinator Script
 * Manages all chat interfaces in the N1O1 application
 * Ensures only one chat interface is active at a time
 * Handles rich content formatting and proper message structure
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat coordination
    initChatCoordination();

    // Set up rich content rendering
    initRichContentProcessing();
});

/**
 * Initialize chat interface coordination to prevent duplicates
 */
function initChatCoordination() {
    // Get all possible chat interfaces
    const chatInterfaces = {
        // NO Molecule chat (from base.html)
        molecule: {
            button: document.getElementById('no-molecule-chat-button'),
            modal: document.getElementById('no-chat-modal'),
            closeBtn: document.getElementById('no-chat-close'),
            expandBtn: document.getElementById('no-chat-expand')
        },

        // Legacy chat widget (from chat_component.html) - if present
        widget: {
            button: document.getElementById('chatToggleBtn'),
            modal: document.getElementById('chatWidget'),
            closeBtn: document.getElementById('chatCloseBtn')
        }
    };

    // Initialize enhanced visualizations and effects
    if (window.N1O1Loader && window.N1O1Loader.generateGasParticles) {
        // Initialize gas particles for NO molecule
        setTimeout(() => {
            try {
                window.N1O1Loader.generateGasParticles();
                console.log("N1O1 gas particle animation initialized");
            } catch (e) {
                console.warn("Could not initialize gas particles:", e);
            }
        }, 1000);
    } else {
        console.log("NO gas particle animations not available");
    }

    // Ensure the NO molecule button is properly visible
    const noButton = document.getElementById('no-molecule-chat-button');
    if (noButton) {
        noButton.style.opacity = '1';
        noButton.style.zIndex = '9999';
    }

    // Identity verification to ensure the chatbot maintains its identity
    const noChatIdentity = {
        name: "N1O1ai",
        role: "clinical trial assistant",
        specialization: "nitric oxide research",
        creator: "JustGoingViral",
        model: "NitroSynt-4",
        greeting: "Hi, I'm N1O1ai! Would you like help with the clinical trial app or guidance on our nitric oxide therapy tools?"
    };


    // Get all buttons that might trigger a chat open
    const allTriggerButtons = [
        document.getElementById('indexChatBtn'),
        document.getElementById('openChatBtn'),
        document.getElementById('chatToggleBtnDesktop')
    ].filter(btn => btn !== null);

    // Check if any chat interface exists
    const hasNOMoleculeChat = chatInterfaces.molecule.button && chatInterfaces.molecule.modal;
    const hasWidgetChat = chatInterfaces.widget.button && chatInterfaces.widget.modal;

    if (hasNOMoleculeChat || hasWidgetChat) {
        // STEP 1: Close all chat interfaces initially
        if (hasNOMoleculeChat) {
            chatInterfaces.molecule.modal.style.display = 'none';
        }

        if (hasWidgetChat) {
            chatInterfaces.widget.modal.style.display = 'none';
        }

        // STEP 2: Setup event listeners for chat buttons
        if (hasNOMoleculeChat) {
            // Listen for clicks on the N1O1 Molecule chat button
            chatInterfaces.molecule.button.addEventListener('click', function() {
                chatInterfaces.molecule.modal.style.display = 'block';

                // If widget chat exists, hide it
                if (hasWidgetChat) {
                    chatInterfaces.widget.modal.style.display = 'none';
                }
            });

            // Close button for molecule chat
            if (chatInterfaces.molecule.closeBtn) {
                chatInterfaces.molecule.closeBtn.addEventListener('click', function() {
                    chatInterfaces.molecule.modal.style.display = 'none';
                });
            }

            // Expand button for molecule chat
            if (chatInterfaces.molecule.expandBtn) {
                chatInterfaces.molecule.expandBtn.addEventListener('click', function() {
                    chatInterfaces.molecule.modal.classList.toggle('fullscreen');
                    if (chatInterfaces.molecule.modal.classList.contains('fullscreen')) {
                        chatInterfaces.molecule.expandBtn.innerHTML = '<i class="fas fa-compress"></i>';
                        expandBtn.title = 'Exit full screen';
                    } else {
                        chatInterfaces.molecule.expandBtn.innerHTML = '<i class="fas fa-expand"></i>';
                        chatInterfaces.molecule.expandBtn.title = 'Expand to full screen';
                    }
                });
            }
        }

        if (hasWidgetChat) {
            // Listen for clicks on the widget chat button
            chatInterfaces.widget.button.addEventListener('click', function() {
                chatInterfaces.widget.modal.style.display = 'block';

                // If molecule chat exists, hide it
                if (hasNOMoleculeChat) {
                    chatInterfaces.molecule.modal.style.display = 'none';
                }
            });

            // Close button for widget chat
            if (chatInterfaces.widget.closeBtn) {
                chatInterfaces.widget.closeBtn.addEventListener('click', function() {
                    chatInterfaces.widget.modal.style.display = 'none';
                });
            }
        }

        // STEP 3: Set up other trigger buttons to open preferred chat
        allTriggerButtons.forEach(button => {
            if (button) {
                button.addEventListener('click', function(e) {
                    e.preventDefault();

                    // Prefer molecule chat if available, otherwise use widget
                    if (hasNOMoleculeChat) {
                        chatInterfaces.molecule.modal.style.display = 'block';
                        if (hasWidgetChat) {
                            chatInterfaces.widget.modal.style.display = 'none';
                        }
                    } else if (hasWidgetChat) {
                        chatInterfaces.widget.modal.style.display = 'block';
                    }
                });
            }
        });
    }
}

/**
 * Markdown-like text processing for messages
 * Supports basic formatting, links, code blocks, and image rendering
 */
function initRichContentProcessing() {
    // Listen for new messages being added
    const chatMessages = document.getElementById('no-chat-messages');

    if (chatMessages) {
        // Add a MutationObserver to process rich content when new messages arrive
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Process all message bubbles for rich content
                    const messageBubbles = chatMessages.querySelectorAll('.no-chat-bubble');
                    messageBubbles.forEach(processRichContent);
                }
            });
        });

        // Start observing
        observer.observe(chatMessages, { childList: true, subtree: true });

        // Process existing messages
        const existingMessages = chatMessages.querySelectorAll('.no-chat-bubble');
        existingMessages.forEach(processRichContent);
    }
}

/**
 * Process rich content in a message bubble
 */
function processRichContent(bubble) {
    if (!bubble || bubble.dataset.processed === 'true') return;

    // Mark as processed to avoid duplicate processing
    bubble.dataset.processed = 'true';

    let content = bubble.innerHTML;

    // 1. Format paragraphs properly with proper spacing
    content = formatParagraphs(content);

    // 2. Process markdown-style formatting
    content = formatMarkdown(content);

    // 3. Process image links
    content = processImageLinks(content);

    // 4. Process code blocks and inline code
    content = processCodeBlocks(content);

    // 5. Convert URLs to clickable links
    content = processLinks(content);

    // Update the content
    bubble.innerHTML = content;

    // Post-processing for any special elements
    processCharts(bubble);
}

/**
 * Format text into proper paragraphs
 */
function formatParagraphs(text) {
    // Replace double line breaks with paragraph tags
    let formatted = text.replace(/\n\s*\n/g, '</p><p>');

    // Wrap in paragraphs if not already
    if (!formatted.startsWith('<p>')) {
        formatted = '<p>' + formatted;
    }
    if (!formatted.endsWith('</p>')) {
        formatted = formatted + '</p>';
    }

    // Replace single line breaks with <br>
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

/**
 * Process basic markdown-like formatting
 */
function formatMarkdown(text) {
    // Bold (**text**)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic (*text*)
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Headers (# Header)
    text = text.replace(/^# (.*?)$/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.*?)$/gm, '<h4>$1</h4>');
    text = text.replace(/^### (.*?)$/gm, '<h5>$1</h5>');

    // Lists
    // Unordered list items
    text = text.replace(/^- (.*?)$/gm, '<li>$1</li>');
    // Ordered list items
    text = text.replace(/^(\d+)\. (.*?)$/gm, '<li>$2</li>');

    // Wrap adjacent list items in ul/ol tags
    let inList = false;
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('<li>') && !inList) {
            lines[i] = '<ul>' + lines[i];
            inList = true;
        } else if (!lines[i].includes('<li>') && inList) {
            lines[i-1] = lines[i-1] + '</ul>';
            inList = false;
        }
    }
    if (inList) {
        lines[lines.length-1] = lines[lines.length-1] + '</ul>';
    }

    return lines.join('\n');
}

/**
 * Process image links to display inline images
 */
function processImageLinks(text) {
    // Image syntax: ![alt text](url)
    const imgRegex = /!\[(.*?)\]\((.*?)\)/g;
    return text.replace(imgRegex, '<img src="$2" alt="$1" class="chat-image">');
}

/**
 * Process code blocks
 */
function processCodeBlocks(text) {
    // Code blocks with triple backticks
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code with single backticks
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    return text;
}

/**
 * Convert URLs to clickable links
 */
function processLinks(text) {
    const urlRegex = /(https?:\/\/[^\s<]+)/g;
    return text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
}

/**
 * Process any chart placeholders in the message
 */
function processCharts(bubble) {
    // Look for chart placeholders with data attributes
    const chartPlaceholders = bubble.querySelectorAll('.chart-placeholder');

    chartPlaceholders.forEach(placeholder => {
        // Get chart data
        let chartData;
        try {
            chartData = JSON.parse(placeholder.dataset.chartData);
        } catch (e) {
            console.error('Invalid chart data:', e);
            return;
        }

        // Create chart container
        const chartContainer = document.createElement('div');
        chartContainer.className = 'chart-container';
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);

        // Replace placeholder with container
        placeholder.parentNode.replaceChild(chartContainer, placeholder);

        // Create chart
        new Chart(canvas, chartData);
    });
}

// Scroll chat to bottom
function scrollChatToBottom() {
    const container = document.querySelector('.chat-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }

    // Also try NO molecule chat container
    const noContainer = document.getElementById('no-chat-messages');
    if (noContainer) {
        noContainer.scrollTop = noContainer.scrollHeight;
    }
}

// Make sendMessage function globally available
window.sendMessage = function() {
    const noInput = document.getElementById('no-chat-input');
    const noSendBtn = document.getElementById('no-chat-send');

    if (noInput && noSendBtn) {
        const message = noInput.value.trim();
        if (message) {
            // Trigger the NO molecule chat send functionality
            noSendBtn.click();
        }
    }
};

// Export necessary functions for external use
window.N1O1Chat = {
    sendMessage: window.sendMessage,
    processRichContent: processRichContent,
    scrollChatToBottom: scrollChatToBottom
};