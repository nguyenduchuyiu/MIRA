# %%
from gtts import gTTS
from io import BytesIO
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Generate TTS audio and store it in memory (BytesIO)
tts = gTTS(text="MIRA can you see me go?", lang='en', tld='com.au')
audio = BytesIO()
tts.write_to_fp(audio)

# Reset the stream position to the start
audio.seek(0)

# Load audio from memory into pygame and play it
pygame.mixer.music.load(audio, "mp3")
pygame.mixer.music.play()

# Wait for the audio to finish playing
while pygame.mixer.music.get_busy():
    continue

