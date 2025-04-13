import torch
import torchaudio
import librosa
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

# Load the pretrained model for emotion classification
model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
processor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)

def recognize_emotion(audio_path):
    EMOTION_LABELS = {
        0: "angry",
        1: "calm",
        2: "disgust",
        3: "fearful",
        4: "happy",
        5: "neutral",
        6: "sad",
        7: "surprised",
        8: "frustrated",
        9: "excited",
        10: "bored"
    }
    # Load audio
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

    inputs = processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_class_id = torch.argmax(logits).item()
    emotion = EMOTION_LABELS[predicted_class_id]
    return emotion, logits

def compute_volume(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    avg_volume_db = 20 * np.log10(np.mean(np.abs(y)))
    return avg_volume_db

if __name__ == "__main__":
    audio_file = "harvard.wav"
    emotion, logits = recognize_emotion(audio_file)
    volume = compute_volume(audio_file)

    print("🎭 Detected Emotion:", emotion)
    print("🔊 Average Volume (dB):", round(volume, 2))
