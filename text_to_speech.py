import os
from TTS.api import TTS

# Initialize the TTS model once (global)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

def get_next_filename(prefix="output", ext="wav", folder="."):
    """Find the next available numbered filename like output_1.wav, output_2.wav, etc."""
    i = 1
    while True:
        filename = os.path.join(folder, f"{prefix}_{i}.{ext}")
        if not os.path.exists(filename):
            return filename
        i += 1

def speak(text: str):
    """Generate speech and save to a uniquely named WAV file."""
    output_path = get_next_filename()
    tts.tts_to_file(text=text, file_path=output_path)
    print(f"[TTS] Saved speech to: {output_path}")
    return output_path