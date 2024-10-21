import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import os
import threading
import pyaudio

load_dotenv()

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class SpeechToText:
    def __init__(self):
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.service_region = os.getenv('AZURE_REGION')  # e.g., "eastus"
        self.total_transcript = ""
        self.push_stream = None
        self.audio_config = None
        self.speech_recognizer = None

    def process_recognition_result(self, evt):
        """Processes the recognized speech result."""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcript = evt.result.text
            print(f"Recognized: {transcript}")
            self.total_transcript += transcript + " "
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for PyAudio to fetch audio data."""
        if self.push_stream:
            self.push_stream.write(in_data)
        return (in_data, pyaudio.paContinue)

    def start(self):
        """Begins streaming from the microphone to the Azure Speech-to-Text API."""
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, 
                                               region=self.service_region,
                                               speech_recognition_language="en-US",)
        
        # Create a push stream
        self.push_stream = speechsdk.audio.PushAudioInputStream()
        self.audio_config = speechsdk.audio.AudioConfig(stream=self.push_stream)

        # Create a speech recognizer
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=self.audio_config)
        self.speech_recognizer.recognized.connect(self.process_recognition_result)

        # Start continuous recognition
        self.speech_recognizer.start_continuous_recognition()

        # Set up PyAudio
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            stream_callback=self.audio_callback)

        print("Speak into your microphone...")
        print("Press Enter to stop...")
        
        # Use a separate thread to wait for user input
        stop_event = threading.Event()
        def wait_for_stop():
            input()
            stop_event.set()
        
        threading.Thread(target=wait_for_stop, daemon=True).start()
        
        try:
            while not stop_event.is_set():
                pass
        finally:
            print("Stopping recognition...")
            audio.terminate()
            stream.stop_stream()
            stream.close()
            self.speech_recognizer.stop_continuous_recognition()
            self.push_stream.close()
            
        temp_total_transcript = self.total_transcript
        self.total_transcript = ""
        return temp_total_transcript

if __name__ == "__main__":
    stt = SpeechToText()
    transcript = stt.start()
    print(f"Generated Transcript: {transcript}")