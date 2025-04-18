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
    
    // Initialize chat widget
    initChatWidget();
});

// Global variables for chat
const MAX_HISTORY_LENGTH = 20;

// Initialize chat widget functionality
function initChatWidget() {
    // Chat elements
    const chatWidget = document.getElementById('chatWidget');
    const chatToggleBtn = document.getElementById('chatToggleBtn');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatMessages = document.getElementById('chatMessages');
    const userMessageInput = document.getElementById('userMessage');
    const sendMessageBtn = document.getElementById('sendMessage');
    const attachFileBtn = document.getElementById('attachFileBtn');
    const chatFileUpload = document.getElementById('chatFileUpload');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    
    // Early return if elements don't exist (chat not on this page)
    if (!chatWidget || !chatToggleBtn) return;
    
    // Load chat history from localStorage
    let chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    
    // Initialize chat state from localStorage
    const chatState = localStorage.getItem('chatWidgetVisible');
    if (chatState === 'visible') {
        chatWidget.style.display = 'flex';
    } else {
        chatWidget.style.display = 'none';
    }
    
    // Restore chat messages from history
    if (chatHistory.length > 0) {
        chatMessages.innerHTML = ''; // Clear default messages
        chatHistory.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = msg.role === 'user' ? 'user-message' : 'assistant-message';
            messageDiv.textContent = msg.content;
            
            if (msg.attachment) {
                const attachmentDiv = document.createElement('div');
                attachmentDiv.className = 'file-attachment';
                
                if (msg.attachment.type.startsWith('image/')) {
                    const img = document.createElement('img');
                    img.src = msg.attachment.dataUrl;
                    img.alt = msg.attachment.name;
                    attachmentDiv.appendChild(img);
                } else {
                    const fileIcon = document.createElement('i');
                    fileIcon.className = 'fas fa-file me-2';
                    const fileName = document.createElement('span');
                    fileName.textContent = msg.attachment.name;
                    
                    attachmentDiv.appendChild(fileIcon);
                    attachmentDiv.appendChild(fileName);
                }
                
                messageDiv.appendChild(attachmentDiv);
            }
            
            chatMessages.appendChild(messageDiv);
        });
        
        // Scroll to bottom
        chatWidget.querySelector('.chat-container').scrollTop = chatWidget.querySelector('.chat-container').scrollHeight;
    }
    
    // Make the chat widget draggable
    const chatHeader = document.getElementById('chatHeader');
    makeDraggable(chatWidget, chatHeader);
    
    // Toggle chat visibility
    chatToggleBtn.addEventListener('click', function() {
        chatWidget.style.display = chatWidget.style.display === 'flex' ? 'none' : 'flex';
        localStorage.setItem('chatWidgetVisible', chatWidget.style.display === 'flex' ? 'visible' : 'hidden');
    });
    
    // Close chat
    chatCloseBtn.addEventListener('click', function() {
        chatWidget.style.display = 'none';
        localStorage.setItem('chatWidgetVisible', 'hidden');
    });
    
    // Add message to chat
    function addMessage(message, type, attachment = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = type === 'user' ? 'user-message' : 'assistant-message';
        messageDiv.textContent = message;
        
        // If there's an attachment (file or image)
        if (attachment) {
            const attachmentDiv = document.createElement('div');
            attachmentDiv.className = 'file-attachment';
            
            // Check if it's an image
            if (attachment.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = attachment.dataUrl;
                img.alt = attachment.name;
                attachmentDiv.appendChild(img);
            } else {
                // For other file types
                const fileIcon = document.createElement('i');
                fileIcon.className = 'fas fa-file me-2';
                const fileName = document.createElement('span');
                fileName.textContent = attachment.name;
                
                attachmentDiv.appendChild(fileIcon);
                attachmentDiv.appendChild(fileName);
            }
            
            messageDiv.appendChild(attachmentDiv);
        }
        
        chatMessages.appendChild(messageDiv);
        chatWidget.querySelector('.chat-container').scrollTop = chatWidget.querySelector('.chat-container').scrollHeight;
        
        // Store message in history
        chatHistory.push({
            role: type === 'user' ? 'user' : 'assistant',
            content: message,
            attachment: attachment
        });
        
        // Limit history length
        if (chatHistory.length > MAX_HISTORY_LENGTH) {
            chatHistory.shift();
        }
        
        // Save to localStorage
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }
    
    // Handle file attachment
    let currentAttachment = null;
    
    attachFileBtn.addEventListener('click', function() {
        chatFileUpload.click();
    });
    
    chatFileUpload.addEventListener('change', function() {
        const file = chatFileUpload.files[0];
        if (file) {
            fileNameDisplay.textContent = file.name;
            
            // Read file content
            const reader = new FileReader();
            
            reader.onload = function(e) {
                currentAttachment = {
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    dataUrl: e.target.result
                };
            };
            
            if (file.type.startsWith('image/')) {
                reader.readAsDataURL(file);
            } else {
                reader.readAsText(file);
            }
        }
    });
    
    // Send message
    function sendMessage() {
        const message = userMessageInput.value.trim();
        if (!message && !currentAttachment) return;
        
        // Add user message to chat
        if (message) {
            addMessage(message, 'user', currentAttachment);
        } else if (currentAttachment) {
            addMessage("I'm sending you a file.", 'user', currentAttachment);
        }
        
        userMessageInput.value = '';
        fileNameDisplay.textContent = '';
        
        // Show loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'assistant-message';
        loadingDiv.innerHTML = '<div class="spinner-border spinner-border-sm text-light" role="status"><span class="visually-hidden">Loading...</span></div> Thinking...';
        chatMessages.appendChild(loadingDiv);
        
        // Send message to AI
        fetch('/api/assistant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory.slice(0, -1), // Exclude the message we just added
                attachment: currentAttachment
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            if (data.status === 'success') {
                addMessage(data.response, 'assistant');
                
                // If there's a plot or visualization in the response
                if (data.plot_url) {
                    const plotAttachment = {
                        name: 'visualization.png',
                        type: 'image/png',
                        dataUrl: data.plot_url
                    };
                    addMessage("Here's the visualization you requested:", 'assistant', plotAttachment);
                }
            } else {
                addMessage('Sorry, I encountered an error: ' + data.message, 'assistant');
            }
            
            // Reset current attachment
            currentAttachment = null;
        })
        .catch(error => {
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            addMessage('Sorry, there was an error communicating with the server.', 'assistant');
            console.error('Error:', error);
            
            // Reset current attachment
            currentAttachment = null;
        });
    }
    
    // Send message on button click
    sendMessageBtn.addEventListener('click', sendMessage);
    
    // Send message on Enter key
    userMessageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// Make an element draggable
function makeDraggable(element, handle) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    if (handle) {
        handle.onmousedown = dragMouseDown;
    } else {
        element.onmousedown = dragMouseDown;
    }
    
    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // Get the mouse cursor position at startup
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // Call a function whenever the cursor moves
        document.onmousemove = elementDrag;
    }
    
    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // Calculate the new cursor position
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // Set the element's new position
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.right = "auto";
        element.style.left = (element.offsetLeft - pos1) + "px";
        element.style.bottom = "auto";
    }
    
    function closeDragElement() {
        // Stop moving when mouse button is released
        document.onmouseup = null;
        document.onmousemove = null;
    }
}
