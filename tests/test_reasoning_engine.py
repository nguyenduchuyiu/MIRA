import os
from google.cloud import generativelanguage_v1beta
from google.oauth2.service_account import Credentials

# Authenticate using your service account JSON file
credentials = Credentials.from_service_account_file("/home/huy/mira-service-account.json")

# Create the client with your credentials
client = generativelanguage_v1beta.GenerativeServiceAsyncClient(credentials=credentials)

# Initialize an empty conversation state
conversation = []

# Build the conversation content
def build_content(role, text):
    """Utility to create text-based conversation content."""
    return generativelanguage_v1beta.Content(
        role=role,
        text=text
    )

# Function to add a message to the conversation and call the model
async def chat_with_gemini(user_input):
    # Add user input to the conversation history
    conversation.append(build_content("user", user_input))
    
    # Create the request object with the conversation history
    request = generativelanguage_v1beta.GenerateContentRequest(
        model="models/gemini-1.5-flash-001",
        contents=conversation,  # Maintain context across multiple turns
        generation_config=generativelanguage_v1beta.GenerationConfig(
            temperature=0.6,
            max_tokens=256,
            top_p=0.9,
            top_k=40
        )
    )

    # Make the request and wait for the response
    response = await client.generate_content(request=request)

    # Extract model's response and print it
    response_text = response.candidates[0].content.parts[0].text
    print("MIRA:", response_text)

    # Add model's response to the conversation history
    conversation.append(build_content("model", response_text))

    return response_text

# Run the chat function asynchronously
if __name__ == "__main__":
    import asyncio

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break  # Exit the chat loop
        asyncio.run(chat_with_gemini(user_input))
