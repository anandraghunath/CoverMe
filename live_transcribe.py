import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile
import queue
import threading
import time

model = whisper.load_model("base")
q = queue.Queue()
recording = True
CHUNK_DURATION = 5  # seconds

def record_audio():
    def callback(indata, frames, time, status):
        if status:
            print("⚠️", status)
        q.put(indata.copy())

    with sd.InputStream(samplerate=16000, channels=1, callback=callback):
        print("🎤 Recording from mic... Press Ctrl+C to stop.")
        while recording:
            sd.sleep(int(CHUNK_DURATION * 1000))

def transcribe_loop():
    while recording:
        audio_data = []
        start_time = time.time()

        while time.time() - start_time < CHUNK_DURATION:
            try:
                chunk = q.get(timeout=0.5)
                audio_data.append(chunk)
            except queue.Empty:
                continue

        if not audio_data:
            continue

        audio_np = np.concatenate(audio_data, axis=0)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wavfile.write(f.name, 16000, audio_np)
            print("🧠 Transcribing...")
            result = model.transcribe(f.name)
            print("💬", result["text"], "\n")

try:
    threading.Thread(target=record_audio).start()
    transcribe_loop()
except KeyboardInterrupt:
    recording = False
    print("\n🛑 Recording stopped")
