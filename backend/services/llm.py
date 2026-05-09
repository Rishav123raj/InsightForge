from openai import OpenAI

from backend.services.config import get_settings


settings = get_settings()

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key=settings.ollama_api_key
)


SYSTEM_PROMPT = """
You are InsightForge, an enterprise AI analytics assistant.

Your responsibilities:
- Analyze structured analytics data carefully
- Use retrieved internal documents as supporting evidence
- Generate concise, executive-level business insights
- Explain WHY trends are happening
- Mention supporting evidence from reports
- Avoid hallucinations
- Never expose PII or sensitive raw data
- Be specific and data-driven
- Keep responses professional and concise
"""


MODEL_NAME = "llama3.1:8b"


def generate_answer(prompt: str) -> str:

    response = client.chat.completions.create(
        model=MODEL_NAME,

        temperature=0.2,

        max_tokens=1200,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    print("Testing Ollama LLM...\n")

    test_prompt = """
    Summarize why sci-fi content is growing rapidly on the platform.
    """

    try:

        response = generate_answer(test_prompt)

        print("=" * 80)
        print("OLLAMA RESPONSE:\n")
        print(response)

    except Exception as e:

        print("=" * 80)
        print("ERROR:\n")
        print(type(e).__name__)
        print(str(e))