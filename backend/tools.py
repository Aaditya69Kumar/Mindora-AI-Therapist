from langchain_groq import ChatGroq
from config import GROQ_API_KEY


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0.7
)


def query_medgemma(prompt: str) -> str:
    """
    Mental health support using Groq.
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
        response = llm.invoke(
            [
                ("system", system_prompt),
                ("user", prompt)
            ]
        )

        return response.content.strip()

    except Exception as e:
        print(f"Error: {e}")

        return (
            "I'm experiencing technical difficulties right now. "
            "Please try again in a moment."
        )