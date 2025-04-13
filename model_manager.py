import os
from dotenv import load_dotenv
import google.generativeai as genai
from TTS.api import TTS
from transformers import pipeline

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise Exception("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=gemini_api_key)

# --- Lazy Singletons ---
_gemini_model = None
_tts_model = None
_sentiment_pipeline = None
_emotion_pipeline = None

def get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        _gemini_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    return _gemini_model

def get_tts_model():
    global _tts_model
    if _tts_model is None:
        _tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
    return _tts_model

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