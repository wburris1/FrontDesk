import io
import numpy as np
from scipy.io.wavfile import write
from elevenlabs.client import ElevenLabs
from ..config import Config

MIN_AUDIO_LENGTH = 0.2 # seconds minimum length of audio to send to llm
MIN_LANG_PROB = 0.2 # minimum language probability to accept input

elevenlabs_client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

def transcribe_audio(audio_chunk: np.ndarray, sample_rate = 16000) -> str:
    """Transcribe audio chunk using ElevenLabs STT."""
    try:
        duration = len(audio_chunk) / sample_rate
        if duration < MIN_AUDIO_LENGTH:
            return None

        with io.BytesIO() as buf:
            write(buf, sample_rate, audio_chunk)
            buf.seek(0)
            resp = elevenlabs_client.speech_to_text.convert(file=buf, model_id="scribe_v2")

        return resp
    except Exception as e:
        print(f"[STT error] {e}")
        return None
    
def is_confident(resp):
    if resp and resp.language_probability < MIN_LANG_PROB:
        return False
    return True