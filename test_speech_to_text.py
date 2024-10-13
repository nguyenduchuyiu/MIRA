from asr import SpeechToText

def test_speech_to_text():
    stt = SpeechToText()
    stt.start_listening()
    
    try:
        print("Listening... Press Ctrl+C to stop.")
        while True:
            text = stt.transcribe()
            if text:
                print(f"Transcribed: {text}")
            else:
                print("No audio detected.")
    except KeyboardInterrupt:
        print("\nTranscription stopped.")
    finally:
        stt.stop_listening()

if __name__ == "__main__":
    test_speech_to_text()
