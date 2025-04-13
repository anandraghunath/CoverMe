import os
from dotenv import load_dotenv
import google.generativeai as genai
from transformers import pipeline
from elevenlabs import Voice, VoiceSettings

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
_eleven_api_key = os.getenv("ELEVEN_API_KEY")


if not gemini_api_key:
    raise Exception("GEMINI_API_KEY not found in environment variables.")

if not _eleven_api_key:
    raise Exception("ELEVEN_API_KEY not found in environment variables.")

_eleven_voice = Voice(
    voice_id="Rachel",  # You can use any available voice
    settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75
    )
)

genai.configure(api_key=gemini_api_key)

# --- Lazy Singletons ---
_gemini_model = None
_eleven_voice = None
_sentiment_pipeline = None
_emotion_pipeline = None

def get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        _gemini_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    return _gemini_model


def get_sentiment_analyzer():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline("sentiment-analysis")
    return _sentiment_pipeline

def get_emotion_analyzer():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        _emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)
    return _emotion_pipeline

def get_tts_model():
    global _eleven_voice
    if _eleven_voice is None:
        _eleven_voice = Voice(
            voice_id="9BWtsMINqrJLrRacOk9x",  # Replace with your preferred voice
            settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75
            )
        )
    return _eleven_voice