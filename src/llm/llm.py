from openai import OpenAI
from ..config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def extract_text(resp):
    try:
        # Grab the first message in output
        msg = resp.output[0]
        # Find the first content item of type text
        for c in msg.content:
            if hasattr(c, "text"):
                return c.text
        return ""
    except (IndexError, AttributeError):
        return ""

def get_llm_response(prompt: str) -> str:
    """Send user transcription to OpenAI and return response."""
    try:
        resp = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=[
                {"role": "system", "content": "You are a helpful front desk assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        text = extract_text(resp)
        return text
    except Exception as e:
        print(f"[LLM error] {e}")
        return "<LLM response error>"