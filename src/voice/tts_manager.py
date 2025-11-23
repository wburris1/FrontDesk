import io
import sounddevice as sd
from elevenlabs.client import ElevenLabs
from src.config import Config

# Initialize APIs
elevenlabs_client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

VOICE_ID = "SAz9YHcvj6GT2YYXdXww" # ElevenLabs voice for River


# -----------------------------
# Generate TTS
# -----------------------------
def text_to_speech(text: str):
    """Generate ElevenLabs TTS audio buffer based on sentiment/style."""
    try:
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=VOICE_ID,
            optimize_streaming_latency=2,
            model_id="eleven_flash_v2_5",
            text=text,
            voice_settings={
                "style": 0,
                "stability": 0.2,
                "similarity_boost": 0.65
            }
        )

        # Convert generator → bytes
        audio_bytes = b"".join(chunk for chunk in audio)

        return audio_bytes
    except Exception as e:
        print(f"[TTS error] {e}")
        return None


# -----------------------------
# Playback
# -----------------------------
def play_audio(audio_bytes: bytes):
    """Play audio returned by ElevenLabs."""
    if not audio_bytes:
        return
    
    # Convert MP3/WAV bytes to numpy samples
    import soundfile as sf
    data, samplerate = sf.read(io.BytesIO(audio_bytes), dtype="float32")

    sd.play(data, samplerate)
    sd.wait()


# -----------------------------
# Main interface
# -----------------------------
def speak(message: str):
    """Voice selection → Generate → Play."""
    audio = text_to_speech(message)
    play_audio(audio)