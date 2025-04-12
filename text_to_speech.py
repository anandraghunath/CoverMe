from fastapi import FastAPI
from fastapi.responses import FileResponse
from TTS.api import TTS

app = FastAPI()

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

@app.get("/speak")
def speak(text: str):
    audio_path = "output.wav"
    tts.tts_to_file(text=text, file_path=audio_path)
    return FileResponse(audio_path, media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("text_to_speech:app", host="127.0.0.1", port=8000, reload=True)