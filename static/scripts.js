// Function to take a picture via API
let transcript = "";
let imagePath = "resources/";

function takePicture() {
    fetch('/take_picture')
        .then(response => {
            if (response.ok) {
                alert('Picture taken and saved!');
            } else {
                alert('Failed to take picture.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error taking picture.');
        });
}

// Function to start listening for MIRA's response
function startListening() {
    return fetch('/record_audio', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            // Display MIRA's response text
            var transcript = data.transcript;
            updateChat(transcript);
            // Check if "see now" is in the response
            if (data.transcript.toLowerCase().includes("see")) {
                console.log("'See' detected, attempting to capture image");
                return fetch('/capture_image', { method: 'GET' })
                    .then(response => {
                        console.log("Received response from /capture_image");
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(capturedData => {
                        console.log("Parsed JSON response:", capturedData);
                        imagePath = capturedData.image_path; // Update imagePath
                        console.log("Updated imagePath:", imagePath);
                        
                        // Now proceed to the /reasoning fetch
                        return fetch(`/reasoning?transcript=${encodeURIComponent(transcript)}&image_path=${encodeURIComponent(imagePath)}`, { method: 'GET' });
                    })
                    .then(response => {
                        return response.json();
                    })
                    .then(data => {
                        document.getElementById('chat').innerText = data.response;
                        return fetch(`/synthesize_voice?text=${encodeURIComponent(data.response)}`, { method: 'GET' });
                    })
                    .then(synthResponse => {
                        if (!synthResponse.ok) {
                            throw new Error('Failed to synthesize voice.');
                        }
                    })
                    .catch(error => {
                        console.error("Error in process:", error);
                    });
            } else {
                return fetch(`/reasoning?transcript=${encodeURIComponent(transcript)}&image_path=${encodeURIComponent("resources/")}`, { method: 'GET' })
            .then(response => {
                return response.json();
            })
            .then(data => {
                document.getElementById('chat').innerText = data.response;
                return fetch(`/synthesize_voice?text=${encodeURIComponent(data.response)}`, { method: 'GET' });
            })
            .then(synthResponse => {
                if (!synthResponse.ok) {
                    throw new Error('Failed to synthesize voice.');
                }
            })
            .catch(error => {
                console.error("Error in process:", error);
            });
            }
        })
}

function updateChat(transcript) {
    const chatElement = document.getElementById('chat');
    chatElement.innerHTML += transcript + '<br>'; // Append new text with a line break
    chatElement.scrollTop = chatElement.scrollHeight; // Scroll to the bottom
}