import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

class TextToSpeech:
    def __init__(self):
        # Load Azure credentials from .env file
        load_dotenv()
        self.azure_speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.azure_region = os.getenv('AZURE_REGION')

        # Initialize Azure Speech Config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.azure_speech_key, region=self.azure_region
        )
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        # Create Speech Synthesizer
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=self.audio_config
        )

    def synthesize(self, text):
        try:
            result = self.speech_synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized successfully!")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")
        except Exception as e:
            print(f"An error occurred during speech synthesis: {str(e)}")
