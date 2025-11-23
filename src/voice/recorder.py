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
GREETING_MESSAGE = "Thank you for calling the Covenant House Health Clinic. How can I help you today?"
UNSURE_MESSAGE = "“I'm sorry, I didn't quite catch that. Could you please say it again?”"

vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

class StreamingRecorder:
    def __init__(self):
        self.frame_size = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
        self.buffer = np.array([], dtype="int16")
        self.speech_buffer = []
        self.silent_frames = 0
        self.last_llm_call_time = 0.0
        self.last_transcript = ""
        self.stop_signal = False

        # Queue and stop event for background LLM worker
        self.llm_queue: "queue.Queue[str]" = queue.Queue(maxsize=8)
        self.stop_event = threading.Event()

        # Initialize LLM manager (keeps conversation/history)
        self.llm_manager = LLMManager(recorder=self)

        self.worker_thread = threading.Thread(target=self.llm_worker, daemon=True)
        self.input_stream = None

    def llm_worker(self):
        # speak(GREETING_MESSAGE)
        while not self.stop_event.is_set():
            try:
                resp = self.llm_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            is_valid = is_confident(resp)

            text = getattr(resp, "text", "") or ""

            if text is None:
                break  # sentinel to exit

            cleaned = text.strip()
            if not cleaned:
                continue

            try:
                if is_valid == False:
                    print("Low confidence.")
                    # speak(UNSURE_MESSAGE)
                else:
                    assistant_response = self.llm_manager.ask(cleaned)
                    print(f"Assistant: {assistant_response}")
                    # speak(assistant_response)
            except Exception as e:
                print(f"[LLM error] {e}")

            self.last_llm_call_time = time.time()
            self.last_transcript = cleaned

    def callback(self, indata, frames, time_info, status):
        self.buffer = np.concatenate([self.buffer, indata[:, 0]])

        while len(self.buffer) >= self.frame_size:
            frame = self.buffer[:self.frame_size]
            self.buffer = self.buffer[self.frame_size:]

            is_speech = vad.is_speech(frame.tobytes(), SAMPLE_RATE)
            if is_speech:
                self.speech_buffer.append(frame)
                self.silent_frames = 0
            elif self.speech_buffer:
                self.silent_frames += 1
                if self.silent_frames >= SILENCE_FRAMES_TO_END:
                    full_audio = np.concatenate(self.speech_buffer)
                    resp = transcribe_audio(full_audio, SAMPLE_RATE)

                    text = getattr(resp, "text", "") or ""

                    if text:
                        cleaned = text.strip()
                        print(f"User said: {cleaned}")

                        try:
                            self.llm_queue.put_nowait(resp)
                        except queue.Full:
                            print("LLM queue full; dropping transcript.")
                    else:
                        print("No transcription available.")
                    # Reset buffers
                    self.speech_buffer = []
                    self.silent_frames = 0

    def start_recording(self):
        print("=== Start speaking. Press Ctrl+C to stop ===")
        self.worker_thread.start()
        self.input_stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype="int16",
            callback=self.callback,
            blocksize=self.frame_size
        )
        self.input_stream.start()

    def stop_recording(self):
        print("\nStopping recording...")
        self.stop_event.set()
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
        try:
            self.llm_queue.put_nowait(None)  # sentinel to exit worker
        except Exception:
            pass
        self.worker_thread.join(timeout=1.0)
        print("Recording stopped.")