import google.generativeai as genai
from TTS.api import TTS
from dotenv import load_dotenv
import os
from transformers import pipeline


load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise Exception("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=gemini_api_key)

sentiment_analyzer = pipeline("sentiment-analysis")
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)


model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)



