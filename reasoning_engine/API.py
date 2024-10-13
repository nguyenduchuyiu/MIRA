import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('API_KEY')

# Configure the API
genai.configure(api_key=API_KEY)

class GeminiAPI:
    def __init__(self):
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_response(self, prompt, max_tokens=100):
        # Set up generation config
        generation_config = GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
        )
        
        # Generate content
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
