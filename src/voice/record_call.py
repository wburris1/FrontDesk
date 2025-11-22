import time
import threading
import queue
import numpy as np
import sounddevice as sd
import webrtcvad
from src.llm.manager import LLMManager
from .stt_manager import transcribe_audio
from .tts_manager import speak
from .stt_manager import is_confident

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 30
VAD_AGGRESSIVENESS = 2
SILENCE_FRAMES_TO_END = 20  # number of silent frames to consider end of speech
GREETING_MESSAGE = "Hi! This is the Covenant House Health Clinic. What can I do for you today?"
UNSURE_MESSAGE = "Sorry, I couldn't quite catch that."

vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

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
    # Initialize LLM manager (keeps conversation/history)
    llm_manager = LLMManager()

    def llm_worker(q: "queue.Queue[str]", stop_evt: threading.Event) -> None:
        nonlocal last_llm_call_time, last_transcript
        speak(GREETING_MESSAGE)

        while not stop_evt.is_set():
            try:
                resp = q.get(timeout=0.5)
            except queue.Empty:
                continue

            is_valid = is_confident(resp)

            text = getattr(resp, "text", "") or ""

            if text is None:
                # sentinel to exit
                break

            cleaned = text.strip()
            if not cleaned:
                continue

            # Call LLM (via LLMManager) outside audio thread
            try:
                if is_valid == False:
                    print("Low confidence.")
                    speak(UNSURE_MESSAGE)
                else:
                    assistant_response = llm_manager.ask(cleaned)
                    print(f"Assistant: {assistant_response}")
                    speak(assistant_response)
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
                    resp = transcribe_audio(full_audio, SAMPLE_RATE)

                    text = getattr(resp, "text", "") or ""

                    if text:
                        cleaned = text.strip()
                        print(f"User said: {cleaned}")

                        # Enqueue transcript for background LLM processing (non-blocking).
                        try:
                            llm_queue.put_nowait(resp)
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
