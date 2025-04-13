# CoverMe
CoverMe was created during Purdue Catapult Hackathon 2025. It is a real-time, AI-powered social assistant that listens to in-person conversations through an earbud and provides smart, context-aware suggestions to help the user navigate the interaction.
# Tech Stack
- Used Whisper for speech-to-text input, ElevenLabs for text-to-speech output, and Resemblyzer and WebRTC VAD to filter out your own voice using speaker recognition and silence detection for backend.
- Employed Gemini API to generate smart suggestions and hugging face for emotion and sentiment detection.
- HTML and JavaScript for the front end.
# Installation Process
- Install FFmpeg
- Install Whisper using pip install git+https://github.com/openai/whisper.git 
- Run pip install -r requirements.txt 
- Run live_audio_stream2.py (change this to when UI is finisihed)
