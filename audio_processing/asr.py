from google.cloud import speech
from .microphone_stream import MicrophoneStream, RATE, CHUNK
from google.api_core.exceptions import GoogleAPICallError

class ASR:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.total_transcript = ""

    def process_responses(self, responses):
        """Processes the streaming responses from the Speech-to-Text API."""
        try:
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript
                print(f"Transcript: {transcript}")

                if result.is_final:
                    print(f"Final Transcript: {transcript}\n")
                    self.total_transcript += transcript + " "
        except Exception as e:
            print(f"Error processing responses: {str(e)}")

    def start(self):
        """Begins streaming from the microphone to the Speech-to-Text API."""
        try:
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code="en-US",
            )
            streaming_config = speech.StreamingRecognitionConfig(
                config=config, interim_results=True
            )

            with MicrophoneStream(RATE, CHUNK) as stream:
                audio_generator = stream.generator()
                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )

                try:
                    responses = self.client.streaming_recognize(
                        config=streaming_config, requests=requests
                    )
                    self.process_responses(responses)
                except GoogleAPICallError as api_error:
                    print(f"Google API error occurred: {str(api_error)}")
                except Exception as e:
                    print(f"An error occurred during streaming: {str(e)}")

        except Exception as e:
            print(f"An error occurred while setting up streaming: {str(e)}")

        return self.total_transcript

    def reset_transcript(self):
        self.total_transcript = ""
