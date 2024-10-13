from audio_processing.asr import ASR
from reasoning_engine.nlu import NLU
from audio_processing.tts import TextToSpeech  # Import the TextToSpeech class

if __name__ == "__main__":
    asr = ASR()
    nlu = NLU()
    tts = TextToSpeech()  # Create an instance of TextToSpeech

    print("Start speaking...")
    transcript = asr.start_streaming()
    
    print(f"Total Text: {transcript}")
    
    response = nlu.process_text(transcript)
    print(f"Gemini Response: {response}")
    
    # Convert the response to speech
    tts.synthesize(response)
