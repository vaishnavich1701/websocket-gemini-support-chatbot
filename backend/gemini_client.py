import os
from dotenv import load_dotenv
from google import genai

# Load .env variables
load_dotenv()

MODEL_NAME = "gemini-3-flash-preview"

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in .env file")

    return genai.Client(api_key=api_key)

def generate_text(
    system_instructions: str,
    user_content: str,
    temperature: float = 0.4,
) -> str:
    """
    Uses Gemini interactions API (preview-compatible).
    System instructions are embedded into the user prompt
    because 'system' role is not supported.
    """
    client = get_client()

    combined_prompt = f"""
SYSTEM INSTRUCTIONS:
{system_instructions}

---

USER MESSAGE:
{user_content}
""".strip()

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=combined_prompt,
        generation_config={
            "temperature": temperature
        }
    )

    # Extract last text output safely
    try:
        return interaction.outputs[-1].text
    except Exception:
        return ""
