from flask import Flask, render_template, request, jsonify, Response
import threading
import time
import os
import queue
import json


# Import your existing modules
import model_manager
from live_audio_stream2 import calibrate_self_voice, listen_and_run
from transcript_to_suggestions import process_transcript_segment
from text_to_speech import speak

# Create templates directory first
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, 'templates')
os.makedirs(templates_dir, exist_ok=True)

# Write the HTML template - removed text input section
with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Live Audio Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        button {
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        #startBtn {
            background-color: #4CAF50;
            color: white;
        }
        #stopBtn {
            background-color: #f44336;
            color: white;
        }
        .conversation {
            height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px 12px;
            border-radius: 8px;
            max-width: 80%;
        }
        .user {
            background-color: #E3F2FD;
            align-self: flex-end;
            margin-left: auto;
        }
        .other {
            background-color: #F5F5F5;
        }
        .ai {
            background-color: #E8F5E9;
        }
        .speaker {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .status {
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }
        .calibration-steps {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f8f8f8;
            display: none;
        }
        .calibration-step {
            margin-bottom: 10px;
        }
        .active-step {
            font-weight: bold;
            color: #2196F3;
        }
        .completed-step {
            color: #4CAF50;
            text-decoration: line-through;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Live Audio Assistant</h1>
        
        <div class="controls">
            <button id="startBtn">Start Listening</button>
            <button id="stopBtn" disabled>Stop Listening</button>
        </div>
        
        <div class="calibration-steps" id="calibrationSteps">
            <h3>Voice Calibration</h3>
            <div class="calibration-step" id="step1">1. Speak sample 1/3 when prompted</div>
            <div class="calibration-step" id="step2">2. Speak sample 2/3 when prompted</div>
            <div class="calibration-step" id="step3">3. Speak sample 3/3 when prompted</div>
        </div>
        
        <div class="conversation" id="conversation">
            <!-- Conversation messages will appear here -->
        </div>
        
        <div class="status" id="status">Ready</div>
    </div>

    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const conversation = document.getElementById('conversation');
        const status = document.getElementById('status');
        const calibrationSteps = document.getElementById('calibrationSteps');
        const step1 = document.getElementById('step1');
        const step2 = document.getElementById('step2');
        const step3 = document.getElementById('step3');
        
        let isListening = false;
        
        startBtn.addEventListener('click', async () => {
            try {
                status.textContent = 'Starting voice calibration...';
                startBtn.disabled = true;
                calibrationSteps.style.display = 'block';
                
                // Add a system message to the conversation
                addMessage('System', 'Voice calibration starting. Please follow the prompts to speak 3 samples.');
                
                const response = await fetch('/start_listening', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    isListening = true;
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    status.textContent = 'Listening...';
                    calibrationSteps.style.display = 'none';
                } else {
                    status.textContent = `Error: ${result.message}`;
                    startBtn.disabled = false;
                    calibrationSteps.style.display = 'none';
                }
            } catch (error) {
                status.textContent = `Error: ${error.message}`;
                startBtn.disabled = false;
                calibrationSteps.style.display = 'none';
            }
        });
        
        stopBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/stop_listening', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    isListening = false;
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    status.textContent = 'Stopped listening';
                } else {
                    status.textContent = `Error: ${result.message}`;
                }
            } catch (error) {
                status.textContent = `Error: ${error.message}`;
            }
        });
        
        function addMessage(speaker, text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${speaker.toLowerCase()}`;
            
            const speakerDiv = document.createElement('div');
            speakerDiv.className = 'speaker';
            speakerDiv.textContent = speaker;
            
            const textDiv = document.createElement('div');
            textDiv.textContent = text;
            
            messageDiv.appendChild(speakerDiv);
            messageDiv.appendChild(textDiv);
            
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }
        
        // Set up event source for conversation updates
        const eventSource = new EventSource('/stream_updates');
        
        eventSource.onmessage = (event) => {
            const newMessages = JSON.parse(event.data);
            
            newMessages.forEach(msg => {
                addMessage(msg.speaker, msg.text);
            });
        };
        
        // Handle calibration events
        const calibrationEventSource = new EventSource('/calibration_updates');
        
        calibrationEventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.step === 1) {
                step1.classList.add('active-step');
                step2.classList.remove('active-step');
                step3.classList.remove('active-step');
            } else if (data.step === 2) {
                step1.classList.remove('active-step');
                step1.classList.add('completed-step');
                step2.classList.add('active-step');
                step3.classList.remove('active-step');
            } else if (data.step === 3) {
                step1.classList.remove('active-step');
                step2.classList.remove('active-step');
                step1.classList.add('completed-step');
                step2.classList.add('completed-step');
                step3.classList.add('active-step');
            } else if (data.step === 'completed') {
                step1.classList.add('completed-step');
                step2.classList.add('completed-step');
                step3.classList.add('completed-step');
                step1.classList.remove('active-step');
                step2.classList.remove('active-step');
                step3.classList.remove('active-step');
                
                // Hide calibration steps after completion
                setTimeout(() => {
                    calibrationSteps.style.display = 'none';
                }, 2000);
            }
            
            if (data.message) {
                addMessage('System', data.message);
            }
        };
        
        calibrationEventSource.onerror = () => {
            console.error('Calibration event source error');
        };
        
        eventSource.onerror = () => {
            status.textContent = 'Connection error. Reconnecting...';
            // EventSource will automatically try to reconnect
        };
    </script>
</body>
</html>
    ''')

# Create Flask app after template is created
app = Flask(__name__, template_folder=templates_dir)

# Global variables
conversation_history = []
is_listening = False
listening_thread = None
calibration_step = 0
calibration_updates = queue.Queue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_listening', methods=['POST'])
def start_listening():
    global is_listening, listening_thread, calibration_step
    
    if is_listening:
        return jsonify({"status": "error", "message": "Already listening"})
    
    # Reset calibration step
    calibration_step = 0
    calibration_updates.put({"step": calibration_step, "message": "Press Enter and speak when prompted for calibration."})
    
    # Start calibration and listening in a separate thread
    listening_thread = threading.Thread(target=calibrate_and_listen)
    listening_thread.daemon = True
    listening_thread.start()
    
    return jsonify({"status": "success", "message": "Starting calibration and listening"})

def calibrate_and_listen():
    global is_listening, calibration_step
    
    try:
        # Replace input() calls in calibrate_self_voice
        original_input = __builtins__.input
        
        def custom_input(prompt):
            global calibration_step
            calibration_step += 1
            
            if "sample 1" in prompt:
                calibration_updates.put({"step": 1, "message": "Speak sample 1/3 now..."})
                time.sleep(1)  # Give UI time to update
                return ""
            elif "sample 2" in prompt:
                calibration_updates.put({"step": 2, "message": "Speak sample 2/3 now..."})
                time.sleep(1)
                return ""
            elif "sample 3" in prompt:
                calibration_updates.put({"step": 3, "message": "Speak sample 3/3 now..."})
                time.sleep(1)
                return ""
            else:
                return original_input(prompt)
        
        __builtins__.input = custom_input
        
        # Run calibration
        try:
            calibrate_self_voice()
            calibration_updates.put({"step": "completed", "message": "Calibration complete. Now listening for conversations."})
        finally:
            # Restore original input function
            __builtins__.input = original_input
        
        # Start listening
        is_listening = True
        listen_and_run()
    except Exception as e:
        print(f"Error in calibrate_and_listen: {e}")
    finally:
        is_listening = False

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    global is_listening
    
    if not is_listening:
        return jsonify({"status": "error", "message": "Not currently listening"})
    
    is_listening = False
    conversation_history.append({
        "speaker": "System",
        "text": "Listening stopped.",
        "timestamp": time.time()
    })
    
    return jsonify({"status": "success", "message": "Stopped listening"})

@app.route('/get_conversation_history')
def get_conversation_history():
    return jsonify(conversation_history)

@app.route('/stream_updates')
def stream_updates():
    def generate():
        last_id = 0
        while True:
            if len(conversation_history) > last_id:
                data = json.dumps(conversation_history[last_id:])
                last_id = len(conversation_history)
                yield f"data: {data}\n\n"
            time.sleep(0.5)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/calibration_updates')
def calibration_updates_stream():
    def generate():
        while True:
            try:
                data = calibration_updates.get(timeout=1)
                yield f"data: {json.dumps(data)}\n\n"
            except queue.Empty:
                time.sleep(0.5)
                continue
    
    return Response(generate(), mimetype='text/event-stream')

# Override the original functions to capture output
def _patched_process_transcript_segment(ctx, new_text):
    try:
        # Add to conversation history first
        conversation_history.append({
            "speaker": "Other",
            "text": new_text,
            "timestamp": time.time()
        })
        
        # Then call the original function to generate a response
        process_transcript_segment(ctx, new_text)
    except Exception as e:
        print(f"Error in patched process_transcript_segment: {e}")
        conversation_history.append({
            "speaker": "System",
            "text": f"Error processing transcript: {e}",
            "timestamp": time.time()
        })

# Override speak function to capture the response
def _patched_speak(text, speed=1.3):
    try:
        # Add AI response to conversation history
        conversation_history.append({
            "speaker": "AI",
            "text": text,
            "timestamp": time.time()
        })
        
        # Call the original speak function
        return speak(text, speed)
    except Exception as e:
        print(f"Error in patched speak: {e}")
        conversation_history.append({
            "speaker": "System",
            "text": f"Error generating speech: {e}",
            "timestamp": time.time()
        })
        return None

# Apply the patches
import transcript_to_suggestions
import text_to_speech
transcript_to_suggestions.process_transcript_segment = _patched_process_transcript_segment
text_to_speech.speak = _patched_speak

if __name__ == '__main__':
    print("Flask app starting on http://127.0.0.1:5000")
    print("Templates directory:", templates_dir)
    app.run(debug=True, host='127.0.0.1', port=5000)