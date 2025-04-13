from fastapi import FastAPI
from model_manager import get_gemini_model, get_tts_model, get_sentiment_analyzer

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Load all models ONCE when the backend starts
    get_gemini_model()
    get_tts_model()
    get_sentiment_analyzer()
    print("✅ Models initialized and ready to go.")

@app.get("/healthcheck")
def check():
    return {"status": "OK"}