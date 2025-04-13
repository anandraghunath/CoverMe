import torch
import torchaudio
import librosa
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
""" how to use:
from audioEmotion import get_emotion_and_volume

emotion, volume = get_emotion_and_volume("harvard.wav")
print("Emotion:", emotion)
print("Avg Volume (dB):", round(volume, 2))
"""

# Load model and processor once when the module is imported
_model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
_model = Wav2Vec2ForSequenceClassification.from_pretrained(_model_name)
_processor = Wav2Vec2FeatureExtractor.from_pretrained(_model_name)

# Manually define labels since model.config.id2label may be incomplete
_EMOTION_LABELS = {
    0: "angry", 1: "calm", 2: "disgust", 3: "fearful", 4: "happy",
    5: "neutral", 6: "sad", 7: "surprised", 8: "frustrated", 9: "excited", 10: "bored"
}

def get_emotion_and_volume(audio_path: str):
    """Returns (emotion_label, average_volume_db) for a given audio file."""

    # --- Emotion Detection ---
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

    inputs = _processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        logits = _model(**inputs).logits
    predicted_class_id = torch.argmax(logits).item()
    emotion = _EMOTION_LABELS.get(predicted_class_id, "unknown")

    # --- Volume Calculation ---
    y, sr = librosa.load(audio_path, sr=None)
    avg_volume_db = 20 * np.log10(np.mean(np.abs(y)))

    return emotion, avg_volume_db
