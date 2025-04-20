
/**
 * Chat Coordinator Script
 * Manages multiple chat interfaces to ensure only one is visible at a time
 * Prevents duplicate chat windows from appearing
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat coordination
    initChatCoordination();
});

function initChatCoordination() {
    // NO Molecule chat (from base.html)
    const noMoleculeButton = document.getElementById('no-molecule-chat-button');
    const noMoleculeModal = document.getElementById('no-chat-modal');
    const noMoleculeChatCloseBtn = document.getElementById('no-chat-close');
    
    // Modern chat widget (from chat_component.html)
    const chatToggleBtn = document.getElementById('chatToggleBtn');
    const chatWidget = document.getElementById('chatWidget');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    
    // If either chat interface exists
    if ((noMoleculeButton && noMoleculeModal) || (chatToggleBtn && chatWidget)) {
        // Store active chat type in localStorage
        let activeChatType = localStorage.getItem('active-chat-type') || 'none';
        
        // Initialize visibility based on stored state
        if (noMoleculeModal) {
            noMoleculeModal.style.display = activeChatType === 'molecule' ? 'block' : 'none';
        }
        
        if (chatWidget) {
            chatWidget.style.display = activeChatType === 'widget' ? 'flex' : 'none';
        }
        
        // NO Molecule Chat Button Click
        if (noMoleculeButton) {
            noMoleculeButton.addEventListener('click', function() {
                // Hide the widget chat if it's open
                if (chatWidget) {
                    chatWidget.style.display = 'none';
                }
                
                // Toggle molecule chat
                noMoleculeModal.style.display = 'block';
                localStorage.setItem('active-chat-type', 'molecule');
            });
        }
        
        // Modern Chat Toggle Button Click
        if (chatToggleBtn) {
            chatToggleBtn.addEventListener('click', function() {
                // Hide the molecule chat if it's open
                if (noMoleculeModal) {
                    noMoleculeModal.style.display = 'none';
                }
                
                // Toggle widget chat
                chatWidget.style.display = chatWidget.style.display === 'flex' ? 'none' : 'flex';
                localStorage.setItem('active-chat-type', chatWidget.style.display === 'flex' ? 'widget' : 'none');
            });
        }
        
        // Close buttons
        if (noMoleculeChatCloseBtn) {
            noMoleculeChatCloseBtn.addEventListener('click', function() {
                noMoleculeModal.style.display = 'none';
                localStorage.setItem('active-chat-type', 'none');
            });
        }
        
        if (chatCloseBtn) {
            chatCloseBtn.addEventListener('click', function() {
                chatWidget.style.display = 'none';
                localStorage.setItem('active-chat-type', 'none');
            });
        }
        
        // Handle other chat buttons
        const openChatBtn = document.getElementById('openChatBtn');
        if (openChatBtn) {
            openChatBtn.addEventListener('click', function() {
                if (chatWidget) {
                    // Prefer modern chat widget
                    chatWidget.style.display = 'flex';
                    localStorage.setItem('active-chat-type', 'widget');
                } else if (noMoleculeModal) {
                    // Fall back to NO molecule chat
                    noMoleculeModal.style.display = 'block';
                    localStorage.setItem('active-chat-type', 'molecule');
                }
            });
        }
        
        // Handle index page chat button
        const indexChatBtn = document.getElementById('indexChatBtn');
        if (indexChatBtn) {
            indexChatBtn.addEventListener('click', function() {
                if (chatWidget) {
                    chatWidget.style.display = 'flex';
                    localStorage.setItem('active-chat-type', 'widget');
                }
            });
        }
    }
}
