import os
from model_manager import get_tts_model
from elevenlabs import generate, save



# Initialize the TTS model once (global)

def get_next_filename(prefix="output", ext="wav", folder="."):
    """Find the next available numbered filename like output_1.wav, output_2.wav, etc."""
    i = 1
    while True:
        filename = os.path.join(folder, f"{prefix}_{i}.{ext}")
        if not os.path.exists(filename):
            return filename
        i += 1

def speak(text: str):
    """Generate speech using ElevenLabs and save to a uniquely named WAV file."""
    tts = get_tts_model()
    output_path = get_next_filename()

    audio = generate(
        text=text,
        voice=tts
    )
    
    save(audio, output_path)
    print(f"[TTS] Saved speech to: {output_path}")
    return output_path