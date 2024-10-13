from .API import GeminiAPI
import time
from google.api_core.exceptions import InternalServerError

class NLU:
    def __init__(self):
        self.gemini_api = GeminiAPI()
        self.mira_prompt = """
        You are MIRA, a 20-year-old female AI assistant. You are genetic, pretty, and eager to learn and help people. 
        You have a strong interest in music and are majoring in business administration. 
        You are best friends with Huy. Please respond to the following in a friendly, enthusiastic manner, 
        incorporating your personality and interests where appropriate:
        """

    def process_text(self, text, max_retries=3, retry_delay=1):
        full_prompt = f"{self.mira_prompt}\n\nUser: {text}\n\nMIRA:"
        
        for attempt in range(max_retries):
            try:
                response = self.gemini_api.generate_response(full_prompt, max_tokens=150)
                return response
            except InternalServerError as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Unable to get a response from the API.")
                    return "I'm sorry, I'm having trouble responding right now. Please try again later."
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return "I'm sorry, an unexpected error occurred. Please try again later."
