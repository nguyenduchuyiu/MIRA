import pyaudio
from six.moves import queue # type: ignore
import time

# Audio recording parameters
RATE = 16000  # Sample rate (16 kHz)
CHUNK = int(RATE / 10)  # 100ms chunks

class MicrophoneStream:
    """Opens a recording stream as a generator yielding audio chunks."""
    def __init__(self, rate, chunk, max_seconds=3):
        self._rate = rate
        self._chunk = chunk
        self._max_seconds = max_seconds

        # Create a buffer to hold audio chunks
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
        start_time = time.time()
        while not self.closed:
            if time.time() - start_time > self._max_seconds:
                self.closed = True
                break
            chunk = self._buff.get()
            if chunk is None:
                return
            yield chunk

if __name__ == "__main__":
    mic = MicrophoneStream(RATE, CHUNK)
    for chunk in mic.generator():
        print(chunk)
