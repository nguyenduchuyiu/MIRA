// Socket connection with error handling
const socket = io('http://localhost:5000', {
    transports: ['websocket'],
    cors: {
        origin: "http://localhost:5000"
    },
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
});

// DOM Elements
const recognizedText = document.getElementById('recognized-text');
const chatElement = document.getElementById('mira-chat');
const statusElement = document.getElementById('status'); 
const microphoneIcon = document.getElementById('microphoneIcon'); 

// State management
let isProcessing = false;
let isListening = false;
let transcript = "";
let imagePath = "resources/";

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateStatus('Connected');
    enableControls(true);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateStatus('Disconnected');
    enableControls(false);
    isListening = false;
    updateButtonState();
    changeIcon('listening-icon', 'microphoneIcon');
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    updateStatus('Connection Error');
    enableControls(false);
    changeIcon('listening-icon', 'microphoneIcon');
});

socket.on('recognizing', (data) => {
    console.log('Interim:', data.text);
    if (recognizedText) {
        recognizedText.innerText = data.text;
    }
});

socket.on('recognized', async (data) => {
    if (isProcessing) {
        console.log('Already processing a transcript');
        return;
    }

    console.log('Final:', data.text);
    transcript = data.text;
    updateChat(transcript);
    
    // First stop recording and update UI
    await stopListening();
    changeIcon('listening-icon', 'mira-icon');
    enableControls(false);
    
    // Then process the transcript
    await processTranscriptWithImage(transcript);
});

// Main control functions
async function startListening() {
    if (isListening) {
        console.log('Already listening');
        return;
    }

    try {
        const response = await fetch('/record_audio');
        const data = await response.json();
        
        if (data.status === "Recording started") {
            isListening = true;
            updateStatus('Listening...');
            updateButtonState();
            changeIcon('microphoneIcon', 'listening-icon');
            console.log('Recording started successfully');
        } else {
            console.log(data.status);
            // Reset icon if start fails
            changeIcon('listening-icon', 'microphoneIcon');
        }
    } catch (error) {
        console.error("Error starting recording:", error);
        updateStatus('Error starting recording');
        // Reset icon on error
        changeIcon('listening-icon', 'microphoneIcon');
    }
}

async function stopListening() {
    if (!isListening) {
        console.log('Not currently listening');
        return;
    }

    try {
        const response = await fetch('/stop_recording');
        const data = await response.json();
        
        if (data.status === "Recording stopped") {
            isListening = false;
            updateStatus('Stopped');
            updateButtonState();
            console.log('Recording stopped successfully');
        }
    } catch (error) {
        console.error("Error stopping recording:", error);
        updateStatus('Error stopping recording');
        // Reset state and UI on error
        isListening = false;
        updateButtonState();
    }
}

// Image handling and transcript processing
async function processTranscriptWithImage(transcript) {
    if (isProcessing) {
        console.log('Already processing transcript');
        return;
    }

    try {
        isProcessing = true;
        if (transcript.toLowerCase().includes("see")) {
            console.log("'See' detected, capturing image...");
            await captureAndProcessImage(transcript);
        } else {
            await processTranscript(transcript, imagePath);
        }
    } catch (error) {
        console.error("Error processing transcript:", error);
        updateStatus('Error processing transcript');
    } finally {
        isProcessing = false;
    }
}

async function captureAndProcessImage(transcript) {
    try {
        const response = await fetch('/capture_image');
        const capturedData = await response.json();
        imagePath = capturedData.image_path;
        console.log("Image captured:", imagePath);
        await processTranscript(transcript, imagePath);
    } catch (error) {
        console.error("Error capturing image:", error);
        updateStatus('Error capturing image');
    }
}

async function processTranscript(transcript, imagePath) {
    try {
        // Process transcript
        const reasoningResponse = await fetch(
            `/reasoning?transcript=${encodeURIComponent(transcript)}&image_path=${encodeURIComponent(imagePath)}`
        );
        const reasoningData = await reasoningResponse.json();
        
        // Update chat with response
        if (chatElement) {
            chatElement.innerText = reasoningData.response;
        }

        // Synthesize voice
        const synthResponse = await fetch(
            `/synthesize_voice?text=${encodeURIComponent(reasoningData.response)}`
        );
        
        if (!synthResponse.ok) {
            throw new Error('Voice synthesis failed');
        }

        // Wait for synthesis to complete before enabling controls
        await synthResponse.blob();
        
        // Reset UI after processing is complete
        changeIcon('mira-icon', 'microphoneIcon');
        enableControls(true);

    } catch (error) {
        console.error("Error in transcript processing:", error);
        updateStatus('Error processing response');
        // Reset UI even if there's an error
        changeIcon('mira-icon', 'microphoneIcon');
        enableControls(true);
    }
}

// UI update functions
function updateChat(text) {
    if (chatElement) {
        const newMessage = document.createElement('div');
        newMessage.className = 'chat-message';
        newMessage.innerHTML = text;
        chatElement.appendChild(newMessage);
        chatElement.scrollTop = chatElement.scrollHeight;
        wrapTextWithGradient();
    }
}

function updateStatus(message) {
    if (statusElement) {
        statusElement.innerText = message;
    }
}

function updateButtonState() {
    if (microphoneIcon) {
        microphoneIcon.disabled = isListening;
    }
}

function enableControls(enabled) {
        microphoneIcon.disabled = !enabled;
}

function wrapTextWithGradient() {
    const text = chatElement.innerHTML;

    // Regex to match emojis (covers a broad range of Unicode emojis)
    const emojiRegex = /([\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])/gu;

    // Split content into parts (text and emojis)
    const parts = text.split(emojiRegex);

    // Reconstruct the content, wrapping only non-emoji parts in <span> tags
    const processedContent = parts
        .map(part =>
            emojiRegex.test(part) ? part : `<span class="gradient-text">${part}</span>`
        )
        .join('');

    // Set the new HTML content
    chatElement.innerHTML = processedContent;
}

function changeIcon(fromId, toId) {
    const fromIcon = document.getElementById(fromId);
    const toIcon = document.getElementById(toId);

    if (!fromIcon || !toIcon) {
        console.error('Icon elements not found:', fromId, toId);
        return;
    }

    fromIcon.style.display = 'none';
    toIcon.style.display = 'block';
}

// Initial setup
updateButtonState();
updateStatus('Ready');
