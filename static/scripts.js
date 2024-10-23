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
const chatElement = document.getElementById('chat');
const statusElement = document.getElementById('status'); // Add this element to your HTML
const startButton = document.getElementById('startButton'); // Add this element to your HTML
const stopButton = document.getElementById('stopButton');  // Add this element to your HTML

// State management
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
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    updateStatus('Connection Error');
    enableControls(false);
});

socket.on('recognizing', (data) => {
    console.log('Interim:', data.text);
    if (recognizedText) {
        recognizedText.innerText = data.text;
    }
});

socket.on('recognized', (data) => {
    console.log('Final:', data.text);
    transcript = data.text;
    updateChat(transcript);
    processTranscriptWithImage(transcript);
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
            console.log('Recording started successfully');
        } else {
            console.log(data.status);
        }
    } catch (error) {
        console.error("Error starting recording:", error);
        updateStatus('Error starting recording');
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
    }
}

// Image handling and transcript processing
async function processTranscriptWithImage(transcript) {
    try {
        if (transcript.toLowerCase().includes("see")) {
            console.log("'See' detected, capturing image...");
            await captureAndProcessImage();
        } else {
            await processTranscript(transcript, imagePath);
        }
    } catch (error) {
        console.error("Error processing transcript:", error);
        updateStatus('Error processing transcript');
    }
}

async function captureAndProcessImage() {
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
    } catch (error) {
        console.error("Error in transcript processing:", error);
        updateStatus('Error processing response');
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
    }
}

function updateStatus(message) {
    if (statusElement) {
        statusElement.innerText = message;
    }
}

function updateButtonState() {
    if (startButton && stopButton) {
        startButton.disabled = isListening;
        stopButton.disabled = !isListening;
    }
}

function enableControls(enabled) {
    if (startButton && stopButton) {
        startButton.disabled = !enabled;
        stopButton.disabled = !enabled || !isListening;
    }
}

// Initial setup
updateButtonState();
updateStatus('Ready');