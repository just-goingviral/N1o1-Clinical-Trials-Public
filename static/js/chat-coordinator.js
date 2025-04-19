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
    const chatToggleBtnDesktop = document.getElementById('chatToggleBtnDesktop');
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
                // Hide the other chat if it's open
                if (chatWidget) {
                    chatWidget.style.display = 'none';
                }
                
                // Show this chat
                noMoleculeModal.style.display = 'block';
                
                // Store active chat type
                localStorage.setItem('active-chat-type', 'molecule');
            });
        }
        
        // NO Molecule Chat Close Button
        if (noMoleculeChatCloseBtn) {
            noMoleculeChatCloseBtn.addEventListener('click', function() {
                noMoleculeModal.style.display = 'none';
                localStorage.setItem('active-chat-type', 'none');
            });
        }
        
        // Modern Chat Toggle Button
        if (chatToggleBtn) {
            chatToggleBtn.addEventListener('click', function() {
                // Hide the other chat if it's open
                if (noMoleculeModal) {
                    noMoleculeModal.style.display = 'none';
                }
                
                // Toggle this chat
                const isVisible = chatWidget.style.display === 'flex';
                chatWidget.style.display = isVisible ? 'none' : 'flex';
                
                // Store active chat type
                localStorage.setItem('active-chat-type', isVisible ? 'none' : 'widget');
            });
        }
        
        // Desktop Chat Button (if exists)
        if (chatToggleBtnDesktop) {
            chatToggleBtnDesktop.addEventListener('click', function() {
                // This button may be connected to the regular toggle button in some templates
                // But we'll add fallback behavior for layouts where it's not
                
                // Hide the other chat if it's open
                if (noMoleculeModal) {
                    noMoleculeModal.style.display = 'none';
                }
                
                if (chatWidget) {
                    // Toggle this chat
                    const isVisible = chatWidget.style.display === 'flex';
                    chatWidget.style.display = isVisible ? 'none' : 'flex';
                    
                    // Store active chat type
                    localStorage.setItem('active-chat-type', isVisible ? 'none' : 'widget');
                }
            });
        }
        
        // Chat Widget Close Button
        if (chatCloseBtn) {
            chatCloseBtn.addEventListener('click', function() {
                chatWidget.style.display = 'none';
                localStorage.setItem('active-chat-type', 'none');
            });
        }
    }
}