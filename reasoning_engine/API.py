import os
import google.generativeai as genai
from google.generativeai import caching
from google.generativeai.types import GenerationConfig
from dotenv import load_dotenv


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

    def initialize_model(self, model_name='models/gemini-1.5-flash-001'):
        # Set up the generation config
        self.generation_config = GenerationConfig(
            temperature=0.9,
            top_p=1,
            top_k=1,
            max_output_tokens=4096
        )
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            system_instruction="You are MIRA, a personal female assistant. Answer concisely. Don't add Mira or User before the response."
        )

    def generate_response(self, prompt, image=None):
        # Include the content buffer in the prompt
        self.append_content_buffer(prompt=prompt, image=image)

        full_prompt = "\n".join(self.content_buffer)
        prompt_list = [full_prompt] + ([image] if image is not None else [])
        print(f"prompt_list: {prompt_list}")
        response = self.model.generate_content(prompt_list)
        # Add the model's response to the buffer
        self.append_content_buffer(response_text=response.text)

        return response.text, response.prompt_feedback

    def reset_cache(self):
        # Reinitialize the model to reset the cache
        self.initialize_model()
        # Clear the buffer
        self.content_buffer.clear()

    def append_content_buffer(self, prompt=None, image=None, response_text=None):
        entries_to_write = []  # List to hold entries for writing

        # Build the conversation buffer
        if prompt is not None:
            entry = f"User: {prompt}"
            self.content_buffer.append(entry)
            entries_to_write.append(entry)
        if response_text is not None:
            entry = f"Mira: {response_text}"
            self.content_buffer.append(entry)
            entries_to_write.append(entry)

        # Limit the content buffer to the most recent 30 entries
        if len(self.content_buffer) > 30:  # 10 user prompts + 10 images + 10 responses
            self.content_buffer.pop(0)  # Remove the oldest entry

        # Write to the file only if there are new entries
        if entries_to_write:
            with open('resources/content_buffer.txt', 'a') as file:
                file.write('\n'.join(entries_to_write) + '\n')

    def load_content_buffer(self):
        # Load the content buffer from a file
        with open('resources/content_buffer.txt', 'r') as file:
            self.content_buffer = file.readlines()




