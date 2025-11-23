from src.voice.recorder import StreamingRecorder
import time

recorder = StreamingRecorder()

def start_stream():
    """Start the recording stream."""
    recorder.start_recording()

def end_stream():
    """Stop the recording stream."""
    recorder.stop_recording()

if __name__ == "__main__":
    try:
        start_stream()

        while not recorder.stop_signal:
            time.sleep(1)
        end_stream()
    except KeyboardInterrupt:
        end_stream()