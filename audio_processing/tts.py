import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import re

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
        # Regular expression to match emojis and '**' characters
        pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]|\\*\\*", flags=re.UNICODE
        )

        # Remove emojis and '**' from the text
        text_without_emojis_and_asterisks = pattern.sub(r'', text)

        try:
            result = self.speech_synthesizer.speak_text_async(text_without_emojis_and_asterisks).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized successfully!")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")
        except Exception as e:
            print(f"An error occurred during speech synthesis: {str(e)}")
