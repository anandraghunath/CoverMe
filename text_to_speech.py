import base64
from fastapi import FastAPI
from TTS.api import TTS

# Initialize FastAPI app
app = FastAPI()

# Load Coqui TTS model (you can choose the model as per your requirements)
# Here, we're using the English model 'tts_models/en/ljspeech/tacotron2-DDC' as an example
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

@app.get("/speak")
def speak(text: str):
    # Generate the speech as an audio file
    audio_path = "output.wav"
    tts.tts_to_file(text=text, file_path=audio_path)

    # Read the audio file as bytes
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()

    # Encode audio bytes to base64
    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
    
    # Return the base64-encoded audio
    return {"audio_base64": encoded_audio}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("text_to_speech:app", host="127.0.0.1", port=8000, reload=True)