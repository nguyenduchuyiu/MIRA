import numpy as np
from microphone_stream import AudioCapture

def main():
    # Initialize the audio capture
    audio_capture = AudioCapture(rate=44100, channels=2, frames_per_buffer=1024)
    
    try:
        # Start the audio stream
        audio_capture.start_stream()
        print("Recording... Press Ctrl+C to stop.")
        
        while True:
            # Read audio data
            data = audio_capture.read_data()
            # Process the data (for now, just print the shape)
            print(f"Captured audio data shape: {data.shape}")
    
    except KeyboardInterrupt:
        # Stop the stream on user interruption
        print("\nRecording stopped.")
    
    finally:
        # Ensure the stream is properly closed
        audio_capture.stop_stream()
        audio_capture.terminate()

if __name__ == "__main__":
    main()