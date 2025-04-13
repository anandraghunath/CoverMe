import io
import os
from model_manager import get_tts_model
from elevenlabs import generate, save
import simpleaudio as sa
from pydub import AudioSegment



def get_next_filename(prefix="output", ext="wav", folder="."):
    """Find the next available numbered filename like output_1.wav, output_2.wav, etc."""
    i = 1
    while True:
        filename = os.path.join(folder, f"{prefix}_{i}.{ext}")
        if not os.path.exists(filename):
            return filename
        i += 1

def play_wav(filepath: str):
    """Play a WAV file using simpleaudio (cross-platform)."""
    try:
        wave_obj = sa.WaveObject.from_wave_file(filepath)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        print(f"[🔊 Played]: {filepath}")
    except Exception as e:
        print(f"❌ Could not play audio: {e}")

def speak(text: str):
    """Generate speech using ElevenLabs and save to a uniquely named WAV file."""
    tts = get_tts_model()
    output_path = get_next_filename()

    # ElevenLabs returns MP3 bytes by default
    audio_bytes = generate(
        text=text,
        voice=tts
    )

    # Convert MP3 bytes to WAV using pydub
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    audio.export(output_path, format="wav")

    print(f"[TTS] Saved speech to: {output_path}")
    play_wav(output_path)

    return output_path