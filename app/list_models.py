import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# List available models
models = client.models.list()

print("Available Gemini models:\n")

for model in models:
    if "generateContent" in (model.supported_actions or []):
        print(model.name)