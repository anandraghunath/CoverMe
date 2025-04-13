import os
import time
from typing import List, Optional
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

class ContextBlock:
    def __init__(self, text: str, speaker: str = "unknown", timestamp: Optional[float] = None):
        self.text = text.strip()
        self.speaker = speaker
        self.timestamp = timestamp or time.time()

    def __str__(self):
        return f"[{self.speaker} @ {time.strftime('%H:%M:%S', time.localtime(self.timestamp))}]: {self.text}"


class ContextWindow:
    def __init__(self, max_blocks: int = 5):
        self.max_blocks = max_blocks
        self.blocks: List[ContextBlock] = []

    def add(self, text: str, speaker: str = "User"):
        block = ContextBlock(text, speaker)
        self.blocks.append(block)
        if len(self.blocks) > self.max_blocks:
            self.blocks.pop(0)

    def get_context_as_text(self, separator: str = "\n") -> str:
        return separator.join(str(block) for block in self.blocks)

    def get_raw_text(self) -> str:
        return " ".join(block.text for block in self.blocks)

    def clear(self):
        self.blocks = []

ctx = ContextWindow(max_blocks = 2)


        
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
            voice_id="onwK4e9ZLuTAKqWW03F9",  # Replace with your preferred voice
            settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75
            )
        )
    return _eleven_voice