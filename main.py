import os 
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user

# Load environment variables
load_dotenv()

# Retrieve the API Key from the environment variable (e.g., from your .env file)
api_key = os.environ.get("BOOT_DEV_GROK_API_KEY")

try:
    # 1. Check for API key presence and initialize the Client
    if not api_key:
        raise ValueError("Configuration Error: API Key not found. Please set BOOT_DEV_GROK_API_KEY in your .env file.")
        
    client = Client(
        api_key=api_key 
    )
    
    # 2. Create a chat instance
    # The 'grok-code-fast-1' model is specifically optimized for code generation and technical reasoning, 
    # making it ideal for your intended use case.
    chat = client.chat.create(
        model="grok-code-fast-1" 
    )
    
    # 3. Add the user message
    chat.append(
        user("Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum.")
    )
    
    # 4. Get the response
    response = chat.sample()
    
    # Extract token usage from the response metadata
    prompt_tokens = response.usage.prompt_tokens
    response_tokens = response.usage.completion_tokens
    
    # 5. Print the Grok response
    print("Grok Technical Response:")
    print(response.content)
    print("\n--- Token Usage ---")
    
    # 6. Print the token counts in the requested format
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")
    print("-------------------")


except ValueError as ve:
    # Handles the specific case where the key is missing
    print(f"{ve}")
except Exception as e:
    # Catches general API or network errors
    print(f"An unexpected error occurred during API interaction: {e}")
