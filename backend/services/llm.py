import logging

from openai import OpenAI

from backend.services.config import get_settings


# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    handlers=[
        logging.FileHandler("insightforge.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("insightforge.llm")


# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------

settings = get_settings()


# -----------------------------------------------------------------------------
# OpenAI / Ollama Client
# -----------------------------------------------------------------------------

def get_client():

    logger.info("Initializing Ollama client")

    return OpenAI(
        base_url="http://host.docker.internal:11434/v1",
        api_key=settings.ollama_api_key or "ollama"
    )


# -----------------------------------------------------------------------------
# System Prompt
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# LLM Generation
# -----------------------------------------------------------------------------

def generate_answer(prompt: str) -> str:

    logger.info("Starting AI answer generation")

    logger.info(f"Using model: {MODEL_NAME}")

    logger.info(f"Prompt length: {len(prompt)} characters")

    try:

        client = get_client()

        logger.info("Sending request to Ollama model")

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

        logger.info("LLM response received successfully")

        answer = response.choices[0].message.content

        logger.info(
            f"Generated response length: {len(answer)} characters"
        )

        return answer

    except Exception as e:

        logger.exception(
            f"LLM generation failed: {str(e)}"
        )

        return (
            "Unable to generate AI insights currently. "
            "Please try again later."
        )


# -----------------------------------------------------------------------------
# Local Testing
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    print("Testing Ollama LLM...\n")

    test_prompt = """
    Summarize why sci-fi content is growing rapidly on the platform.
    """

    try:

        logger.info("Running standalone LLM test")

        response = generate_answer(test_prompt)

        print("=" * 80)
        print("OLLAMA RESPONSE:\n")
        print(response)

    except Exception as e:

        logger.exception(
            f"Standalone LLM test failed: {str(e)}"
        )

        print("=" * 80)
        print("ERROR:\n")
        print(type(e).__name__)
        print(str(e))