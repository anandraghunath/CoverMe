import os
import time
from typing import List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from transformers import pipeline
#from text_to_speech import speak

# --- Load API Key from .env ---
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise Exception("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=gemini_api_key)

# --- Sentiment & Emotion Analyzers ---
sentiment_analyzer = pipeline("sentiment-analysis")
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

# --- Context Manager Classes ---

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

# --- Emotion + Sentiment + Rule-Based Fallback ---

def analyze_emotion(text: str):
    sentiment = sentiment_analyzer(text)[0]
    emotion = emotion_analyzer(text)[0][0]
    return sentiment['label'], sentiment['score'], emotion['label'], emotion['score']

def fallback_response(emotion_label: str):
    responses = {
        "anger": "Sounds like you're upset. Want to talk more about it?",
        "disgust": "Sounds like you're upset. Want to talk more about it?",
        "joy": "That's great to hear!",
        "sadness": "I'm sorry you're feeling this way. I'm here if you want to talk.",
        "surprise": "Wow, that sounds unexpected. What happened?",
        "fear": "That sounds scary. Is there anything I can do to help?",
    }
    return responses.get(emotion_label.lower(), "Thanks for sharing. Can you tell me more?")

# --- Gemini Suggestion Generator ---

def generate_suggestion_with_gemini(context_text: str, mode: str = "Friendly") -> str:
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
        prompt = (
            f"You are a highly adaptive conversational assistant who helps users respond "
            f"intelligently, empathetically, or playfully during real-time conversations.\n\n"
            f"Given the following conversation so far, suggest one short but helpful response the user could say in response."
            f"For example, if a person was getting yelled at, you should give a suggestion like 'I suggest you confirm their feelings and explain how you feel as well to better communicate'\n\n"
            f"Conversation:\n{context_text}\n\n"
            f"Suggested Next Line:"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini Error]: {e}")
        return None

# --- Master Processor ---

def process_transcript_segment(ctx: ContextWindow, new_text: str, speaker: str = "Other", mode: str = "Witty"):
    ctx.add(new_text, speaker)
    context_text = ctx.get_context_as_text()
    sentiment, sentiment_score, emotion, emotion_score = analyze_emotion(new_text)

    # Fallback for negative emotions
    if emotion.lower() in ["anger", "disgust", "fear", "sadness"]:
        response = fallback_response(emotion)
        source = "Fallback"
    else:
        response = generate_suggestion_with_gemini(context_text, mode)
        if response:
            source = "Gemini"
        else:
            response = fallback_response(emotion)
            source = "Fallback (Gemini Failed)"

    print(f"\n🎤 Speaker: {speaker}")
    print(f"\nText: {new_text}")
    print(f"🧠 Detected Sentiment: {sentiment} ({sentiment_score:.2f})")
    print(f"🎭 Detected Emotion: {emotion} ({emotion_score:.2f})")
    print(f"💬 Suggestion Source: {source}")
    print(f"✅ Suggested Response: {response}")
    #speak(response)
    

# --- Example Usage ---

if __name__ == "__main__":
    ctx = ContextWindow(max_blocks=5)

    # Simulate conversation
    process_transcript_segment(ctx, "Trump is currently president right now right?", speaker="Other")
    process_transcript_segment(ctx, "Who cares?", speaker="User")
    process_transcript_segment(ctx, "Okay… I just wanted to know bro.", speaker="Other")
    process_transcript_segment(ctx, "Wanna discuss this later?", speaker="User", mode="Friendly")
