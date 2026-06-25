import ollama
import requests


def query_medgemma(prompt: str) -> str:
    """
    Calls MedGemma model.
    """

    system_prompt = """
You are Dr. Emily Hartman, a warm and experienced clinical psychologist.

Respond with:
- empathy
- validation
- practical guidance
- open ended questions

Never use labels.
Keep responses conversational.
"""

    try:
        response = ollama.chat(
            model="medgemma:4b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 350
            }
        )

        return response["message"]["content"].strip()

    except Exception:
        return (
            "I'm experiencing technical difficulties right now. "
            "Please try again in a moment."
        )


