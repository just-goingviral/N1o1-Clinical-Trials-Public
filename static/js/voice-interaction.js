/**
 * N1O1 Voice Interaction Module
 * Handles voice recording and transcription for the application
 */

// Global variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Check browser compatibility with audio recording
function checkAudioSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('Browser does not support audio recording');
        return false;
    }
    return true;
}

// Start audio recording
function startRecording() {
    if (!checkAudioSupport()) {
        alert('Your browser does not support audio recording');
        return;
    }

    if (isRecording) return;
    isRecording = true;

    // Get user media with audio
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            // Determine which audio format to use based on browser support
            let mimeType = 'audio/webm';

            // Check for Safari/iOS which needs different format
            const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
            const isiOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

            if (isSafari || isiOS) {
                mimeType = 'audio/mp4';
            }

            // Create media recorder with appropriate options
            const options = { mimeType: mimeType };
            try {
                mediaRecorder = new MediaRecorder(stream, options);
            } catch (e) {
                // Fallback if the specific mime type isn't supported
                console.warn('Preferred mime type not supported, using default');
                mediaRecorder = new MediaRecorder(stream);
            }

            audioChunks = [];

            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', () => {
                // Create blob with appropriate type
                const audioType = isSafari || isiOS ? 'audio/mp4' : 'audio/webm';
                const audioBlob = new Blob(audioChunks, { type: audioType });

                // Process the recording
                transcribeAudio(audioBlob);

                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());

                isRecording = false;

                // Remove visual feedback
                const recordingIndicator = document.getElementById('recording-indicator');
                if (recordingIndicator) {
                    recordingIndicator.remove();
                }

                // Update UI buttons
                const voiceButtons = document.querySelectorAll('.voice-btn');
                voiceButtons.forEach(btn => btn.classList.remove('recording'));
            });

            mediaRecorder.start();

            // Update UI to show recording status
            const voiceButtons = document.querySelectorAll('.voice-btn');
            voiceButtons.forEach(btn => btn.classList.add('recording'));

            // Add visual feedback
            const messageArea = document.getElementById('no-chat-messages');
            if (messageArea) {
                const recordingIndicator = document.createElement('div');
                recordingIndicator.id = 'recording-indicator';
                recordingIndicator.className = 'recording-indicator';
                recordingIndicator.innerHTML = '<div class="recording-pulse"></div> Recording... <span class="text-muted">(Click microphone to stop)</span>';
                messageArea.appendChild(recordingIndicator);
                messageArea.scrollTop = messageArea.scrollHeight;
            }
        })
        .catch(err => {
            console.error('Error accessing microphone:', err);
            alert('Could not access your microphone. Please check your microphone permissions.');
            isRecording = false;
        });
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    isRecording = false;
}

// Toggle recording state
function toggleRecording(element) {
    if (isRecording) {
        stopRecording();
        element.classList.remove('recording');
    } else {
        startRecording();
        element.classList.add('recording');
    }
}

// Transcribe audio using the server API
function transcribeAudio(audioBlob) {
    // Create visual indicator for transcription process
    const transcriptionStatus = document.getElementById('transcriptionStatus');
    if (transcriptionStatus) {
        transcriptionStatus.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Transcribing audio...';
        transcriptionStatus.style.display = 'block';
    }

    // Prepare form data with proper filename and extension
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    // Send to server for transcription
    fetch('/notes/api/transcribe', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Handle successful transcription
            if (transcriptionStatus) {
                transcriptionStatus.innerHTML = '<i class="fas fa-check-circle text-success me-2"></i> Transcription complete';
                setTimeout(() => {
                    transcriptionStatus.style.display = 'none';
                }, 3000);
            }

            // Get the target textarea to append transcription
            const noteContent = document.getElementById('content');
            if (noteContent) {
                // Add a new line if there's existing content
                if (noteContent.value && !noteContent.value.endsWith('\n\n')) {
                    noteContent.value += '\n\n';
                }

                // Add the transcribed text
                noteContent.value += data.text;

                // Focus the textarea and move cursor to end
                noteContent.focus();
                noteContent.selectionStart = noteContent.value.length;
                noteContent.selectionEnd = noteContent.value.length;
            }

            // Also check for chat input to append transcription
            const chatInput = document.getElementById('no-chat-input');
            if (chatInput) {
                chatInput.value = data.text;
                chatInput.focus();
            }
        } else {
            // Handle transcription error
            if (transcriptionStatus) {
                transcriptionStatus.innerHTML = `<i class="fas fa-exclamation-circle text-danger me-2"></i> ${data.error || 'Transcription failed'}`;
                setTimeout(() => {
                    transcriptionStatus.style.display = 'none';
                }, 5000);
            }
        }
    })
    .catch(error => {
        console.error('Transcription error:', error);
        if (transcriptionStatus) {
            transcriptionStatus.innerHTML = '<i class="fas fa-exclamation-circle text-danger me-2"></i> Error connecting to transcription service';
            setTimeout(() => {
                transcriptionStatus.style.display = 'none';
            }, 5000);
        }
    });
}

// Initialize voice buttons when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set up voice recording buttons in notes
    const voiceButtons = document.querySelectorAll('.voice-btn');
    voiceButtons.forEach(button => {
        button.addEventListener('click', function() {
            toggleRecording(this);
        });
    });

    // Set up voice recording in chat if present
    const chatVoiceBtn = document.getElementById('no-chat-voice');
    if (chatVoiceBtn) {
        chatVoiceBtn.addEventListener('click', function() {
            toggleRecording(this);
        });
    }
});


/**
 * Voice Interaction with N1O1 Chatbot
 * Allows users to speak to the chatbot and get voice responses
 */

// Prevent duplicate declaration
if (typeof isRecording === 'undefined') {
    let isRecording = false;
}
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

function sendTranscribedText(text) {
    const chatInput = document.getElementById('no-chat-input');
    const sendButton = document.getElementById('no-chat-send');

    if (chatInput && sendButton) {
        chatInput.value = text;

        // Use global sendMessage if available, otherwise click button
        if (typeof window.sendMessage === 'function') {
            window.sendMessage();
        } else {
            sendButton.click();
        }

        // Add feedback to user
        showRecordingFeedback('Message sent!', 'success');
    } else {
        showRecordingFeedback('Chat interface not found', 'error');
    }
}

function showRecordingFeedback(message, type) {
    // Add your feedback implementation here
    console.log(`Recording Feedback: ${message} (${type})`); // Placeholder
}