import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from main import record_video
from reasoning_engine.nlu import NLU
from response_generation.gtts import GTextToSpeech
from visual_processing.vision import VisionProcessing
from audio_processing.asr import ASR

app = Flask(__name__)

# Initialize components
nlu = NLU()
gtts = GTextToSpeech()
vision = VisionProcessing()
asr = ASR()

@app.route('/')
def home():
    """Render the main web interface."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    """Handle requests from the frontend."""
    transcript = asr.start()
    image_path = ''  # Initialize image_path

    if "can" in transcript.lower() and "see" in transcript.lower():
        video_path = record_video(duration=3)
        if not video_path:
            return jsonify({'response': "Failed to record video."})

        image_path = vision.analyze_image(video_path)
        return jsonify({'response': "Analyzed image.", 'image_path': image_path})

    elif "i have no questions" in transcript.lower():
        response = "OK, Ask me anything if you want!"
        gtts.synthesize(response)
        return jsonify({'response': response})

    response = nlu.process(transcript, image_path)
    gtts.synthesize(response)
    return jsonify({'response': response})

@app.route('/resources/<path:filename>')
def serve_resources(filename):
    """Serve static resources such as videos or images."""
    return send_from_directory('resources', filename)

if __name__ == '__main__':
    app.run(debug=True)
