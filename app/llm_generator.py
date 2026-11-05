
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found in .env file")

client = genai.Client(api_key=api_key)


def generate_answer(question, context):

    prompt = f"""
You are an AI Personal Study Assistant.

Your task is to help students understand their study materials.

STRICT RULES:

1. Answer using only the provided study material.
2. Do not add facts from your own knowledge.
3. Do not invent information or examples.
4. If the answer is not available in the material,
   clearly say:
   "This information is not available in the uploaded study material."
5. Explain answers in simple, student-friendly English.
6. Use bullet points when they improve readability.
7. Keep the answer focused on the student's question.
8. Do not repeat the entire study material.

STUDY MATERIAL:
{context}

STUDENT QUESTION:
{question}

ANSWER:
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return "I couldn't generate an answer. Please try again."

    except errors.APIError as error:

        print("Gemini API error:", error)

        return (
            "Gemini is temporarily unavailable. "
            "Please try again in a few minutes."
        )
