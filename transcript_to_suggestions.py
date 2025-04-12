import time
from typing import List, Optional
import openai
from transformers import pipeline

# Initialize APIs
openai.api_key = "your-api-key-here"  # Replace this with your env-based key setup
sentiment_analyzer = pipeline("sentiment-analysis")
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

# --- Context Block Manager ---

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
    emotion = emotion_analyzer(text)[0]
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

# --- GPT-4 Suggestion Generator ---

def generate_suggestion(context_text: str, mode: str = "Friendly") -> str:
    system_prompt = f"You are a {mode.lower()} conversational assistant. Based on the recent conversation, suggest one helpful or clever response the user could say next."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conversation:\n{context_text}\n\nSuggestion:"}
            ],
            temperature=0.8,
            max_tokens=50
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[LLM Error]: {e}")
        return None


# --- Master Function ---

def process_transcript_segment(ctx: ContextWindow, new_text: str, speaker: str = "Other", mode: str = "Witty"):
    ctx.add(new_text, speaker)

    context_text = ctx.get_context_as_text()
    sentiment, sentiment_score, emotion, emotion_score = analyze_emotion(new_text)

    # Check emotion and decide: fallback or LLM
    if emotion.lower() in ["anger", "disgust", "fear", "sadness"]:
        response = fallback_response(emotion)
        source = "Fallback"
    else:
        response = generate_suggestion(context_text, mode=mode)
        if response:
            source = "LLM"
        else:
            response = fallback_response(emotion)
            source = "Fallback (LLM Failed)"

    print(f"\n🎤 Speaker: {speaker}")
    print(f"🧠 Detected Sentiment: {sentiment} ({sentiment_score:.2f})")
    print(f"🎭 Detected Emotion: {emotion} ({emotion_score:.2f})")
    print(f"💬 Suggestion Source: {source}")
    print(f"✅ Suggested Response: {response}")

# --- Example Usage ---

if __name__ == "__main__":
    ctx = ContextWindow(max_blocks=5)

    # Simulate a live feed
    process_transcript_segment(ctx, "I can't believe you'd say that. Whatever.", speaker="Other")
    process_transcript_segment(ctx, "Sorry, I didn’t mean it that way.", speaker="User")
    process_transcript_segment(ctx, "Okay… I just need some space.", speaker="Other")
    process_transcript_segment(ctx, "Do you want to talk later?", speaker="User", mode="Friendly")
