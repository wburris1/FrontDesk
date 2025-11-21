import io
import time
import threading
import queue
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import webrtcvad
from elevenlabs.client import ElevenLabs
from ..config import Config
from ..llm.llm import get_llm_response

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 30
VAD_AGGRESSIVENESS = 2
SILENCE_FRAMES_TO_END = 5  # number of silent frames to consider end of speech
MIN_AUDIO_LENGTH = 0.2     # seconds, minimum audio to send to STT
LLM_COOLDOWN = 2.0  # seconds minimum between LLM calls for new transcripts

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

# -----------------------------
# Helper functions
# -----------------------------
def transcribe_audio(audio_chunk: np.ndarray) -> str:
    """Transcribe audio chunk using ElevenLabs STT."""
    try:
        duration = len(audio_chunk) / SAMPLE_RATE
        if duration < MIN_AUDIO_LENGTH:
            print(f"[STT] Audio too short ({duration:.2f}s), skipping...")
            return None

        with io.BytesIO() as buf:
            write(buf, SAMPLE_RATE, audio_chunk)
            buf.seek(0)
            resp = elevenlabs_client.speech_to_text.convert(file=buf, model_id="scribe_v2")

        return getattr(resp, "text", "") or ""
    except Exception as e:
        print(f"[STT error] {e}")
        return None

# -----------------------------
# Streaming VAD + Recorder
# -----------------------------
def run_streaming():
    print("=== Start speaking. Press Ctrl+C to stop ===")

    frame_size = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
    buffer = np.array([], dtype="int16")
    speech_buffer = []
    silent_frames = 0
    last_llm_call_time = 0.0
    last_transcript = ""

    # Queue and stop event for background LLM worker
    llm_queue: "queue.Queue[str]" = queue.Queue(maxsize=8)
    stop_event = threading.Event()

    def llm_worker(q: "queue.Queue[str]", stop_evt: threading.Event) -> None:
        nonlocal last_llm_call_time, last_transcript
        while not stop_evt.is_set():
            try:
                text = q.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:
                # sentinel to exit
                break

            cleaned = text.strip()
            if not cleaned:
                continue

            now = time.time()
            if cleaned == last_transcript:
                print("Duplicate transcript; skipping LLM call.")
                continue
            if (now - last_llm_call_time) < LLM_COOLDOWN:
                print("LLM cooldown active; skipping LLM call.")
                continue

            # Call LLM outside audio thread
            try:
                assistant_reply = get_llm_response(cleaned)
                print(f"Assistant: {assistant_reply}")
            except Exception as e:
                print(f"[LLM error] {e}")

            last_llm_call_time = time.time()
            last_transcript = cleaned

    # start background worker
    worker_thread = threading.Thread(target=llm_worker, args=(llm_queue, stop_event), daemon=True)
    worker_thread.start()

    def callback(indata, frames, time, status):
        nonlocal buffer, speech_buffer, silent_frames
        nonlocal last_llm_call_time, last_transcript
        buffer = np.concatenate([buffer, indata[:, 0]])

        while len(buffer) >= frame_size:
            frame = buffer[:frame_size]
            buffer = buffer[frame_size:]

            is_speech = vad.is_speech(frame.tobytes(), SAMPLE_RATE)
            if is_speech:
                speech_buffer.append(frame)
                silent_frames = 0
            elif speech_buffer:
                silent_frames += 1
                if silent_frames >= SILENCE_FRAMES_TO_END:
                    full_audio = np.concatenate(speech_buffer)
                    text = transcribe_audio(full_audio)
                    if text:
                        cleaned = text.strip()
                        print(f"User said: {cleaned}")

                        # Enqueue transcript for background LLM processing (non-blocking).
                        try:
                            llm_queue.put_nowait(cleaned)
                        except queue.Full:
                            print("LLM queue full; dropping transcript.")
                    else:
                        print("No transcription available.")
                    # Reset buffers
                    speech_buffer = []
                    silent_frames = 0

    try:
        with sd.InputStream(channels=CHANNELS,
                            samplerate=SAMPLE_RATE,
                            dtype="int16",
                            callback=callback,
                            blocksize=frame_size):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        # signal worker to stop and wait for it
        stop_event.set()
        try:
            # put sentinel to ensure worker exits promptly
            llm_queue.put_nowait(None)
        except Exception:
            pass
        worker_thread.join(timeout=1.0)

if __name__ == "__main__":
    run_streaming()
