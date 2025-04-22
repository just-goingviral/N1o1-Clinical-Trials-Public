
/**
 * Voice Interaction with N1O1 Chatbot
 * Allows users to speak to the chatbot and get voice responses
 */

let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let recognizedText = "";

document.addEventListener('DOMContentLoaded', function() {
    // Initialize voice interaction
    initVoiceInteraction();
});

function initVoiceInteraction() {
    // Add voice button to chat interface
    const chatInput = document.getElementById('no-chat-input');
    const chatForm = document.getElementById('no-chat-form');
    
    if (!chatInput || !chatForm) return;
    
    // Create voice button
    const voiceButton = document.createElement('button');
    voiceButton.type = 'button';
    voiceButton.id = 'voice-chat-button';
    voiceButton.className = 'btn voice-btn';
    voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
    voiceButton.title = 'Speak to N1O1ai';
    
    // Insert voice button before send button
    const sendButton = chatForm.querySelector('button[type="submit"]');
    if (sendButton) {
        chatForm.insertBefore(voiceButton, sendButton);
    } else {
        chatForm.appendChild(voiceButton);
    }
    
    // Add event listener to voice button
    voiceButton.addEventListener('click', toggleVoiceRecording);
}

function toggleVoiceRecording() {
    const voiceButton = document.getElementById('voice-chat-button');
    
    if (!isRecording) {
        // Start recording
        startRecording();
        isRecording = true;
        voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
        voiceButton.classList.add('recording');
    } else {
        // Stop recording
        stopRecording();
        isRecording = false;
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.classList.remove('recording');
    }
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                transcribeAudio(audioBlob);
                
                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            });
            
            mediaRecorder.start();
            
            // Add visual feedback
            const messageArea = document.getElementById('no-chat-messages');
            if (messageArea) {
                const recordingIndicator = document.createElement('div');
                recordingIndicator.id = 'recording-indicator';
                recordingIndicator.className = 'recording-indicator';
                recordingIndicator.innerHTML = '<div class="recording-pulse"></div> Recording... <span class="text-muted">(Click microphone to stop)</span>';
                messageArea.appendChild(recordingIndicator);
            }
        })
        .catch(err => {
            console.error('Error accessing microphone:', err);
            alert('Could not access your microphone. Please check your microphone permissions.');
            
            // Reset button state
            const voiceButton = document.getElementById('voice-chat-button');
            if (voiceButton) {
                voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
                voiceButton.classList.remove('recording');
            }
            isRecording = false;
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    
    // Remove recording indicator
    const recordingIndicator = document.getElementById('recording-indicator');
    if (recordingIndicator) {
        recordingIndicator.innerHTML = '<div class="processing-indicator"></div> Processing audio...';
    }
}

function transcribeAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    // Display status in chat
    showTranscriptionStatus('Transcribing your message...');
    
    fetch('/api/transcribe-chat', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showTranscriptionStatus('Error: ' + data.error, true);
            return;
        }
        
        // Set the transcribed text to the input field
        const chatInput = document.getElementById('no-chat-input');
        if (chatInput) {
            chatInput.value = data.text;
            
            // Remove transcription status
            removeTranscriptionStatus();
            
            // If auto-send is enabled, send the message
            if (data.text && data.text.trim() !== '') {
                const chatForm = document.getElementById('no-chat-form');
                if (chatForm) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }
        }
    })
    .catch(error => {
        console.error('Error transcribing audio:', error);
        showTranscriptionStatus('Could not transcribe audio. Please try again.', true);
    });
}

function showTranscriptionStatus(message, isError = false) {
    // Remove existing status
    removeTranscriptionStatus();
    
    // Create status element
    const messageArea = document.getElementById('no-chat-messages');
    if (messageArea) {
        const statusElement = document.getElementById('recording-indicator') || document.createElement('div');
        statusElement.id = 'transcription-status';
        statusElement.className = isError ? 'transcription-error' : 'transcription-status';
        statusElement.innerText = message;
        messageArea.appendChild(statusElement);
    }
}

function removeTranscriptionStatus() {
    const statusElement = document.getElementById('recording-indicator') || document.getElementById('transcription-status');
    if (statusElement) {
        statusElement.remove();
    }
}
