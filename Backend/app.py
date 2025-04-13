from flask import Flask, jsonify

import src.live_audio_stream2

app = Flask(__name__)

@app.route("/start")
def start_process():
    src.calibrate_self_voice()
    src.listen_and_run()
    return jsonify({"message": "Process started!"})

app.run(debug=True)
