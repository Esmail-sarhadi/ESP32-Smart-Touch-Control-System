import random
import time
from datetime import datetime
from flask import Flask, request, jsonify
from paho.mqtt import client as mqtt_client
from collections import deque

broker = 'broker.emqx.io'
port = 1883
topic_touch_state = "esmail/touch_state"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

app = Flask(__name__)
mqtt_client_obj = None

# State management
last_touch_state = False
last_sender = ""

# History management
state_history = deque(maxlen=100)  # Keep last 100 states
schedules = []  # Store schedules

class StateRecord:
    def __init__(self, state, sender, timestamp=None):
        self.state = state
        self.sender = sender
        self.timestamp = timestamp or datetime.now().isoformat()

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(topic_touch_state)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(client, userdata, msg):
        global last_touch_state, last_sender
        message = msg.payload.decode()
        print(f"Received message: {message}")
        
        # Parse message (format: "deviceId:state")
        try:
            parts = message.split(":")
            if len(parts) == 2:
                last_sender = parts[0]
                new_state = parts[1] == "1"
                
                # Only update if state changed
                if new_state != last_touch_state:
                    last_touch_state = new_state
                    # Record state change
                    state_history.append(StateRecord(new_state, last_sender))
        except Exception as e:
            print(f"Error processing message: {e}")

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    return client

@app.route('/')
def index():
    with open('templates/index.html', 'r', encoding='utf-8') as file:
        return file.read()

@app.route('/send_touch', methods=['POST'])
def send_touch():
    try:
        data = request.json
        state = data.get('state', False)
        if mqtt_client_obj:
            message = f"WebApp:{1 if state else 0}"
            mqtt_client_obj.publish(topic_touch_state, message)
            # Record state change
            state_history.append(StateRecord(state, "WebApp"))
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "MQTT client not connected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_state')
def get_state():
    return jsonify({
        "state": last_touch_state,
        "sender": last_sender
    })

@app.route('/get_history')
def get_history():
    try:
        # Convert deque to list of dictionaries
        history_list = [{
            "state": record.state,
            "sender": record.sender,
            "timestamp": record.timestamp
        } for record in state_history]
        
        return jsonify({
            "status": "success",
            "history": history_list
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/schedules', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_schedules():
    global schedules
    
    try:
        if request.method == 'GET':
            return jsonify({"status": "success", "schedules": schedules})
            
        elif request.method == 'POST':
            new_schedule = request.json
            # Validate schedule data
            if all(k in new_schedule for k in ["time", "state", "active"]):
                schedules.append(new_schedule)
                return jsonify({"status": "success", "message": "Schedule added"})
            return jsonify({"status": "error", "message": "Invalid schedule data"})
            
        elif request.method == 'PUT':
            data = request.json
            if "index" in data and "schedule" in data:
                index = data["index"]
                if 0 <= index < len(schedules):
                    schedules[index] = data["schedule"]
                    return jsonify({"status": "success", "message": "Schedule updated"})
                return jsonify({"status": "error", "message": "Invalid index"})
            return jsonify({"status": "error", "message": "Invalid data format"})
            
        elif request.method == 'DELETE':
            index = request.json.get("index")
            if index is not None and 0 <= index < len(schedules):
                schedules.pop(index)
                return jsonify({"status": "success", "message": "Schedule deleted"})
            return jsonify({"status": "error", "message": "Invalid index"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def check_schedules():
    """Check and execute scheduled tasks"""
    global last_touch_state
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        for schedule in schedules:
            if schedule["active"] and schedule["time"] == current_time:
                if last_touch_state != schedule["state"]:
                    message = f"Schedule:{1 if schedule['state'] else 0}"
                    mqtt_client_obj.publish(topic_touch_state, message)
                    
        time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    mqtt_client_obj = connect_mqtt()
    mqtt_client_obj.loop_start()
    
    # Start schedule checker in a separate thread
    from threading import Thread
    schedule_thread = Thread(target=check_schedules, daemon=True)
    schedule_thread.start()
    
    app.run(host='0.0.0.0', port=5000)
