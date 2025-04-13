from fastapi import FastAPI
from contextlib import asynccontextmanager
from model_manager import (
    get_gemini_model,
    get_tts_model,
    get_sentiment_analyzer,
    get_emotion_analyzer,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize models on startup
    get_gemini_model()
    get_tts_model()
    get_sentiment_analyzer()
    get_emotion_analyzer()
    print("✅ Models initialized and ready to go.")
    
    yield  # ← this allows the app to run
    
    # Optional: Cleanup logic here if needed on shutdown

app = FastAPI(lifespan=lifespan)

@app.get("/healthcheck")
def check():
    return {"status": "OK"}