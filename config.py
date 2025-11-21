import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")

    @staticmethod
    def validate():
        missing = []
        if not Config.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not Config.ELEVENLABS_API_KEY:
            missing.append("ELEVENLABS_API_KEY")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}.\n"
                f"Make sure they are defined in your .env file."
            )

# Validate immediately when imported
Config.validate()