import os
import numpy as np
import sounddevice as sd
import webrtcvad
from resemblyzer import VoiceEncoder, preprocess_wav
import whisper
import tempfile
import scipy.io.wavfile as wavfile
from transcript_to_suggestions import process_transcript_segment
import model_manager 

# ==== CONFIG ====
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # ms
VAD_MODE = 1
MAX_SILENT_FRAMES = int(1000 / FRAME_DURATION)
WHISPER_MODEL_NAME = "tiny.en"
CALIBRATION_SEGMENTS = 3
MIN_SEGMENT_DURATION = 1.5  # seconds

# ==== LOAD MODELS ====
print("🔁 Loading models...")
vad = webrtcvad.Vad(VAD_MODE)
encoder = VoiceEncoder()
whisper_model = whisper.load_model(WHISPER_MODEL_NAME)

frame_len_samples = int(SAMPLE_RATE * FRAME_DURATION / 1000)
self_voiceprint = None

def calibrate_self_voice():
    global self_voiceprint
    print(f"🎤 Say something {CALIBRATION_SEGMENTS} times (2 seconds each) to calibrate your voice...")

    embeddings = []
    for i in range(CALIBRATION_SEGMENTS):
        input(f"👉 Press ENTER and speak sample {i + 1}/{CALIBRATION_SEGMENTS}...")
        audio = sd.rec(int(2 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        sd.wait()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wavfile.write(f.name, SAMPLE_RATE, audio)
            wav_path = f.name

        wav = preprocess_wav(wav_path)
        emb = encoder.embed_utterance(wav)
        embeddings.append(emb)

    self_voiceprint = np.mean(embeddings, axis=0)
    print("✅ Calibration complete.")

def get_voiceprint_and_transcribe(audio_data):
    duration = len(audio_data) / SAMPLE_RATE
    if duration < MIN_SEGMENT_DURATION:
        print(f"⚠️ Skipping short segment ({duration:.2f}s)")
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wavfile.write(f.name, SAMPLE_RATE, audio_data)
        wav_path = f.name

    wav = preprocess_wav(wav_path)
    speaker_vec = encoder.embed_utterance(wav)
    similarity = np.dot(self_voiceprint, speaker_vec) / (
        np.linalg.norm(self_voiceprint) * np.linalg.norm(speaker_vec)
    )

    if similarity > 0.75:
        print("🙅 Skipping: this sounds like you.")
        return

    print("💬 Transcribing with Whisper...")
    result = whisper_model.transcribe(wav_path)
    print("\n🗣️ Other speaker:", result["text"])
    process_transcript_segment(model_manager.ctx, result)

def listen_and_run():
    print("🎧 Listening... Press Ctrl+C to stop.")

    buffer = []
    silent_frames = 0

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
            while True:
                chunk, _ = stream.read(frame_len_samples)
                chunk = np.squeeze(chunk)

                if len(chunk) != frame_len_samples:
                    continue

                is_speech = vad.is_speech(chunk.tobytes(), SAMPLE_RATE)
                buffer.append(chunk)

                if is_speech:
                    silent_frames = 0
                else:
                    silent_frames += 1

                if silent_frames >= MAX_SILENT_FRAMES and len(buffer) > 0:
                    print("🧠 Pause detected.")
                    full_audio = np.concatenate(buffer)
                    get_voiceprint_and_transcribe(full_audio)
                    buffer.clear()
                    silent_frames = 0

    except KeyboardInterrupt:
        print("\n🛑 Stopped.")

if __name__ == "__main__":
    calibrate_self_voice()

    listen_and_run()
