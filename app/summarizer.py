
from llm_generator import client
from google.genai import errors


def summarize_document(pages):

    document_text = "\n\n".join(
        f"Page {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    prompt = f"""
You are an AI Personal Study Assistant.

Create a structured summary of this study material.

Requirements:
- Use clear headings.
- Explain important concepts.
- Include key definitions.
- Use bullet points.
- Use simple English.
- Do not invent information.
- Use only the supplied material.

STUDY MATERIAL:
{document_text}

SUMMARY:
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return "Gemini returned an empty response."

    except errors.APIError as error:

        print("\nGEMINI API ERROR:", repr(error))

        return f"Gemini API error: {error}"

    except Exception as error:

        print("\nUNEXPECTED ERROR:", repr(error))

        return f"Unexpected error: {error}"
