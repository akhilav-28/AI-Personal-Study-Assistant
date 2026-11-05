
from llm_generator import client
from google.genai import errors


def generate_revision_questions(pages):

    # Combine extracted PDF pages
    document_text = "\n\n".join(
        f"Page {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    prompt = f"""
You are an AI exam preparation assistant.

Generate revision questions using only the provided study material.

SECTION 1: MULTIPLE CHOICE QUESTIONS

- Generate 5 MCQs.
- Provide 4 options (A, B, C, D).
- Mark the correct answer.
- Give a short explanation.

SECTION 2: SHORT ANSWER QUESTIONS

- Generate 5 short-answer questions.
- Provide clear answers.
- Keep each answer around 2-5 sentences.
- Focus on definitions and important concepts.

SECTION 3: LONG ANSWER QUESTIONS

- Generate 3 long-answer questions.
- Provide structured answers.
- Use headings and bullet points.
- Include explanations of important concepts.
- Write answers suitable for university examinations.

IMPORTANT RULES:

1. Use only the uploaded study material.
2. Do not invent facts or definitions.
3. Avoid duplicate questions.
4. Use simple, student-friendly English.
5. Include answers for every question.
6. If the material is insufficient, generate fewer questions.

STUDY MATERIAL:

{document_text}

GENERATED REVISION QUESTIONS:
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return "Unable to generate revision questions."

    except errors.APIError as error:

        print("Gemini API error:", repr(error))

        return (
            "Gemini is temporarily unavailable. "
            "Please try again later."
        )

    except Exception as error:

        print("Unexpected error:", repr(error))

        return f"Unexpected error: {error}"
