from speechbrain.inference.classifiers import EncoderClassifier
## not working
# Fresh download into new path
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    savedir="tmp/emotion_model"
)

# Must exist and be a valid mono 16kHz .wav file
audio_path = "harvard.wav"

# Run prediction
out_prob, score, index, emotion = classifier.classify_file(audio_path)

print(f"Predicted Emotion: {emotion}")
print(f"Confidence Score: {score.item():.4f}")
