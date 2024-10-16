import numpy as np
import pyaudio
from six.moves import queue # type: ignore
import time

# Audio recording parameters
RATE = 16000  # Sample rate (16 kHz)
CHUNK = int(RATE / 10)  # 100ms chunks
SILENCE_THRESHOLD = 20 # Number of silent chunks before closing (2 seconds)

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

            # Check if the chunk contains only noise
            if self._is_silent(chunk):
                silent_chunks += 1
                if silent_chunks > SILENCE_THRESHOLD:
                    print("Silence detected. Closing stream...")
                    self.__exit__(None, None, None)  # Close the stream on silence
                    return
            else:
                silent_chunks = 0  # Reset on speech activity

    def _is_silent(self, chunk):
        # Convert chunk to NumPy array and compute mean energy
        audio_data = np.frombuffer(chunk, dtype=np.int16)
        mean_energy = np.abs(audio_data).mean()
        normalized_energy = mean_energy / np.iinfo(np.int16).max  # Normalize to range [0, 1]
        return normalized_energy < 0.02  # This mean major of energy come from noise

if __name__ == "__main__":
    mic = MicrophoneStream(RATE, CHUNK)
    for chunk in mic.generator():
        print(chunk)
