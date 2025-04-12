import transformers
from transformers import pipeline
import torch

# Load sentiment and emotion detection pipelines
sentiment_analyzer = pipeline("sentiment-analysis")
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

# Function to detect tone and suggest a response
def analyze_and_respond(text):
    sentiment = sentiment_analyzer(text)[0]
    emotion = emotion_analyzer(text)[0]

    label = emotion[0]['label']
    response = ""

    # Basic rule-based response suggestion
    if label in ["anger", "disgust"]:
        response = "Sounds like you're upset. Want to talk more about it?"
    elif label == "joy":
        response = "That's great to hear!"
    elif label == "sadness":
        response = "I'm sorry you're feeling this way. I'm here if you want to talk."
    elif label == "surprise":
        response = "Wow, that sounds unexpected. What happened?"
    elif label == "fear":
        response = "That sounds scary. Is there anything I can do to help?"
    else:
        response = "Thanks for sharing. Can you tell me more?"

    # Output result
    print(f"Original Message: {text}")
    print(f"Detected Sentiment: {sentiment['label']} ({sentiment['score']:.2f})")
    print(f"Detected Emotion: {label} ({emotion[0]['score']:.2f})")
    print(f"Suggested Response: {response}")

# Example usage
analyze_and_respond(input("What is the message?\n"))
