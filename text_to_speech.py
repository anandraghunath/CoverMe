from TTS.api import TTS

# Initialize the TTS model once (global)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

def speak(text: str, output_path: str = "output.wav"):
    """Generate speech and save to a WAV file."""
    tts.tts_to_file(text=text, file_path=output_path)
    print(f"[TTS] Saved speech to: {output_path}")
    return output_path