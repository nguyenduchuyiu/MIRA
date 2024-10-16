from .API import GeminiAPI
import time
from google.api_core.exceptions import InternalServerError

class NLU:
    def __init__(self):
        # Initialize the GeminiAPI instance
        self.gemini_api = GeminiAPI()
        self.conversation_history = []

    def process(self, text, scenario='', max_retries=3, retry_delay=1):
        for attempt in range(max_retries):
            try:
                # Generate response using the GeminiAPI
                response, usage_metadata = self.gemini_api.generate_response(text, scenario)
                # Log token usage for monitoring
                print(f"Token usage: {usage_metadata}")
                
                return response
            except InternalServerError as e:
                # Handle internal server errors with retries
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Unable to get a response from the API.")
                    return "I'm sorry, I'm having trouble responding right now. Please try again later."
            except Exception as e:
                # Handle any other unexpected errors
                print(f"An unexpected error occurred: {str(e)}")
                return "I'm sorry, an unexpected error occurred. Please try again later."

    def reset_conversation(self):
        # Reset the conversation by reinitializing the cache in GeminiAPI
        self.gemini_api.reset_cache()
        # Clear the conversation history
        self.conversation_history = []
