import os
import google.generativeai as genai
from google.generativeai import caching
from google.generativeai.types import GenerationConfig
import datetime
from dotenv import load_dotenv
import base64

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('API_KEY')

# Configure the API with the obtained key
genai.configure(api_key=API_KEY)

class GeminiAPI:
    def __init__(self):
        # Initialize a buffer to accumulate content
        self.content_buffer = []
        # Initialize the model
        self.initialize_model()

    def initialize_model(self, model_name='models/gemini-1.5-flash-001', cache_ttl=2):
        # Set up the generation config
        self.generation_config = GenerationConfig(
            temperature=0.9,
            top_p=1,
            top_k=1,
            max_output_tokens=4096
        )
        
        # Initialize the model
        self.model = genai.GenerativeModel(model_name=model_name,
                                           generation_config=self.generation_config)


    def generate_response(self, prompt, scenario=''):
        # Add the user's question to the buffer
        self.content_buffer.append(f"User: {prompt}")
        
        # Correct the prompt construction
        prompt = (
            "Pretend that you are MIRA, a female assistant, eager to learn and help. "
            "Your responses should be friendly, knowledgeable, and concise. Strive to provide accurate information, "
            "engage in conversations across various topics"
            "Maintain a positive, supportive tone to make users feel comfortable and valued. "
            "Pretend that you can acttually hear"
            "Understand the information and answer the question based on the following scenario: {scenario}".format(scenario=scenario) if scenario != "" else "",
            "Pretend that you can actually see"
            + " My question: "
            + prompt
        )
        
        # Generate the response
        response = self.model.generate_content(prompt)
        
        # Extract the text from the response
        response_text = response.text

        # Add the model's response to the buffer
        self.content_buffer.append(f"MIRA: {response_text}")

        # Save the content buffer to a file if it's large
        # Check if the total token count exceeds the minimum threshold
        self.append_content_buffer()

        # Get token usage metadata
        usage_metadata = response.prompt_feedback

        return response_text, usage_metadata

    def reset_cache(self):
        # Reinitialize the model to reset the cache
        self.initialize_model()
        # Clear the buffer
        self.content_buffer.clear()

    def append_content_buffer(self):
        # Save the content buffer to a file
        with open('resources/content_buffer.txt', 'a') as file:
            file.write('\n'.join(self.content_buffer))
            file.write('\n')

    def load_content_buffer(self):
        # Load the content buffer from a file
        with open('resources/content_buffer.txt', 'r') as file:
            self.content_buffer = file.readlines()
