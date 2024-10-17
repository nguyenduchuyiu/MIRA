import numpy as np
import pyaudio
from scipy.signal import butter, lfilter
from six.moves import queue  # type: ignore
import wave

# Audio recording parameters
RATE = 20000  # Sample rate (20 kHz)
CHUNK = int(RATE / 10)  # 100ms chunks
SILENCE_THRESHOLD = 20  # Number of silent chunks before closing (2 seconds)

def butter_bandpass(lowcut, highcut, fs, order=5):
    """Design a bandpass filter."""
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Apply bandpass filter to audio data."""
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return lfilter(b, a, data)

class MicrophoneStream:
    """Opens a recording stream as a generator yielding audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

        # Initialize the PyAudio stream
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,  # 16-bit PCM
            channels=1,              # Mono
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Callback function that adds audio chunks to the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()
        

    def generator(self):
        """Yields audio chunks from the buffer."""
        silent_chunks = 0  # Counter for consecutive silent chunks
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return

            yield chunk

            if self._is_silent(chunk):
                silent_chunks += 1
                if silent_chunks > SILENCE_THRESHOLD:
                    print("Silence detected. Closing stream...")
                    self.__exit__(None, None, None)  # Close the stream on silence
                    return
            else:
                silent_chunks = 0  # Reset on speech activity

    def _is_silent(self, chunk):
        """Check if the audio data is silent."""
        # Convert chunk to NumPy array
        audio_data = np.frombuffer(chunk, dtype=np.int16)

        # Apply bandpass filter (100-300 Hz)
        filtered_data = apply_bandpass_filter(
            audio_data, lowcut=100, highcut=300, fs=self._rate, order=5
        )
        mean_energy = np.abs(filtered_data).mean()
        
        normalized_energy = mean_energy / np.iinfo(np.int16).max  # Normalize to [0, 1]
        
        with open('sound.txt', 'a') as file:
            file.write(f"{normalized_energy}\n")
        
        # Adjusted threshold based on distribution analysis
        return normalized_energy < 0.004  # Change threshold as necessary

if __name__ == "__main__":
    mic = MicrophoneStream(RATE, CHUNK)
    for chunk in mic.generator():
        print("Processing filtered chunk...")
