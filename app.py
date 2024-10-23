from imutils.video import VideoStream
from flask import Response, jsonify, request
from flask import Flask
from flask import render_template
from flask_socketio import SocketIO, emit
import azure.cognitiveservices.speech as speechsdk

import threading
import datetime
import imutils
import time
import cv2
import os

from audio_processing.speech_to_text import SpeechToText
from reasoning_engine.nlu import NLU
from response_generation.gtts import GTextToSpeech
from visual_processing.vision import VisionProcessing
from response_generation.tts import TextToSpeech




# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") 

# initialize 
vs = VideoStream(src=0).start()
time.sleep(2.0)
nlu = NLU()
gtts = GTextToSpeech()
tts = TextToSpeech()
vision_processing = VisionProcessing()
# Create speech config and recognizer globally
speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("AZURE_SPEECH_KEY"),  
    region=os.environ.get("AZURE_REGION"))

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, 
    audio_config=audio_config
)


@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")



def detect_motion():
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock
	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it   
		frame = vs.read()
		# Adjust the width and height for rendering
		frame = imutils.resize(frame, width=800)  # Increased width
		# Optionally, you can set height directly if needed
		frame = imutils.resize(frame, height=500)  # Example for height adjustment
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()


   
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')


  
@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media 	
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
 
 

@app.route("/capture_image")
def capture_image():
	global outputFrame, lock
	with lock:
		if outputFrame is not None:
			# Create a filename with the current timestamp
			filename = os.path.join('resources/images', f"picture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
				# Save the current frame as an image
			cv2.imwrite(filename, outputFrame)
			print(f"Picture taken and saved as {filename}")  # Debugging output
			return jsonify({"image_path": filename}), 200
		else:
			print("No frame available!")  # Debugging output
			return jsonify({"image_path": "resources/"}), 400



# @app.route("/record_audio")
# def record_audio():
#     transcript = speech_to_text.start()
#     return jsonify({"transcript": transcript}), 200



@app.route("/reasoning")
def reasoning():
	transcript = request.args.get('transcript', default='', type=str)
	image_path = request.args.get('image_path', default='', type=str)
	response = nlu.process(transcript, image_path)
	return jsonify({"response": response}), 200



@app.route("/synthesize_voice")
def synthesize_voice():
    text = request.args.get('text', default='', type=str)
    if text:
        # gtts.synthesize(text)
        tts.synthesize(text)
        return jsonify({"message": "Voice synthesized successfully!"}), 200
    else:
        return jsonify({"error": "No text provided!"}), 400
    
    
    
# Flag to track recognition status
is_recognizing = False

@app.route('/record_audio')
def record_audio():
    """Start recording when this endpoint is called."""
    global is_recognizing
    if not is_recognizing:
        is_recognizing = True
        socketio.start_background_task(recognize_speech)
        return jsonify({"status": "Recording started"})
    return jsonify({"status": "Already recording"})

def recognize_speech():
    """Handle continuous speech recognition."""
    global speech_recognizer, is_recognizing
    
    def on_recognizing(evt):
        """Handler for intermediate recognition results."""
        socketio.emit('recognizing', {'text': evt.result.text})

    def on_recognized(evt):
        """Handler for final recognition results."""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            socketio.emit('recognized', {'text': evt.result.text})

    def on_canceled(evt):
        """Handler for recognition cancellation."""
        global is_recognizing
        is_recognizing = False
        print(f"Speech recognition canceled: {evt.reason}")
        if evt.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {evt.error_details}")

    # Connect event handlers
    speech_recognizer.recognizing.connect(on_recognizing)
    speech_recognizer.recognized.connect(on_recognized)
    speech_recognizer.canceled.connect(on_canceled)
    
    # Start recognition
    speech_recognizer.start_continuous_recognition()

@app.route('/stop_recording')
def stop_recording():
    """Stop the recording process."""
    global is_recognizing
    if is_recognizing:
        speech_recognizer.stop_continuous_recognition()
        is_recognizing = False
        return jsonify({"status": "Recording stopped"})
    return jsonify({"status": "Not recording"})

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    global is_recognizing
    if is_recognizing:
        speech_recognizer.stop_continuous_recognition()
        is_recognizing = False
    print("Client disconnected")



# check to see if this is the main thread of execution
if __name__ == '__main__':
	# start a thread that will perform motion detection
	t = threading.Thread(target=detect_motion)
	t.daemon = True
	t.start()
	try:
		# start the flask app
		socketio.run(app, use_reloader=False, debug=True)
		# app.run(host='0.0.0.0', port=5000, debug=True)
	except Exception as e:
		print(f"Error starting the app: {e}")
	finally:
		# release the video stream pointer
		vs.stop()

     
