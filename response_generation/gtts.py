import re
import pygame
from io import BytesIO
from gtts import gTTS

class GTextToSpeech:
    def __init__(self):
        pygame.mixer.init()

    def synthesize(self, text):
        filter_text = self.filter_text(text)
        tts = gTTS(text=filter_text, lang='en', tld='com.au')
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        pygame.mixer.music.load(audio, "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        
    def filter_text(self, text):
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
        filter_text = pattern.sub(r'', text)
        return filter_text