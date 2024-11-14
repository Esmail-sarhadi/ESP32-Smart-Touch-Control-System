# 🔮 ESP32 Smart Touch Control System

An interactive IoT project that combines ESP32's touch sensing capabilities with a modern web interface for remote control and monitoring. The system features real-time state synchronization, scheduling capabilities, and a responsive UI with dark mode support.

## 📑 Table of Contents
- [✨ Features](#features)
- [🛠️ Technology Stack](#technology-stack)
- [⚙️ Installation](#installation)
- [🚀 Usage](#usage)
- [🌐 Web Interface](#web-interface)
- [📡 MQTT Communication](#mqtt-communication)
- [📱 API Endpoints](#api-endpoints)
- [⏰ Scheduling System](#scheduling-system)
- [🔧 Configuration](#configuration)
- [🐞 Troubleshooting](#troubleshooting)

## ✨ Features

- **Touch Sensing**: Utilizes ESP32's capacitive touch sensing capabilities
- **Real-time Control**: Instant state synchronization across all connected devices
- **Web Interface**:
  - Modern, responsive design
  - Dark/Light theme toggle
  - RTL support for Persian language
  - Interactive touch control
  - Real-time status updates
- **History Tracking**: Visual representation of state changes over time
- **Scheduling System**: Set automated state changes with time-based triggers
- **MQTT Integration**: Reliable message broker communication
- **Multi-device Support**: Unique device identification and state tracking

## 🛠️ Technology Stack

- **Hardware**:
  - ESP32 Development Board
  - Touch sensor (using GPIO4/T0)
  - LED indicator (using GPIO2)
  
- **Backend**:
  - Python Flask server
  - Paho MQTT client
  - SQLite for data persistence
  
- **Frontend**:
  - HTML5/CSS3/JavaScript
  - Animate.css for animations
  - Responsive design with CSS Grid/Flexbox
  
- **Communication**:
  - MQTT protocol for real-time messaging
  - RESTful API for web interface
  - WebSocket for live updates

## ⚙️ Installation

1. **ESP32 Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/esmail-sarhadi/ESP32-Smart-Touch-Control-System
   
   # Open esp32_touch.ino in Arduino IDE
   # Install required libraries:
   # - PubSubClient
   # - WiFi
   ```

2. **Server Setup**:
   ```bash
   # Navigate to server directory
   cd server
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Start the server
   python app.py
   ```

3. **Configuration**:
   - Update WiFi credentials in `esp32_touch.ino`
   - Configure MQTT broker settings in both ESP32 and server code
   - Adjust touch sensitivity threshold if needed

## 🚀 Usage

1. Upload the ESP32 code to your device
2. Start the Python server
3. Access the web interface at `http://localhost:5000`
4. Touch the sensor or use the web interface to control the state

## 🌐 Web Interface

The web interface provides:
- Touch state toggle button
- Real-time status indicator
- Device connection status
- Historical state changes visualization
- Schedule management interface
- Theme customization

## 📡 MQTT Communication

Messages follow the format: `deviceId:state`
- `deviceId`: Unique identifier for each ESP32
- `state`: 1 (touched) or 0 (released)

Topic: `esmail/touch_state`

## 📱 API Endpoints

```
GET  /get_state      - Get current touch state
POST /send_touch     - Update touch state
GET  /get_history    - Retrieve state history
GET  /schedules      - Get all schedules
POST /schedules      - Create new schedule
PUT  /schedules      - Update existing schedule
DEL  /schedules      - Delete schedule
```

## ⏰ Scheduling System

Create automated state changes with:
- Time selection
- State toggle
- Active/Inactive status
- Persistence across sessions

## 🔧 Configuration

Key configuration options:
```cpp
// ESP32
#define TOUCH_PIN T0    // Touch sensor pin
#define LED_PIN 2       // Status LED pin
#define THRESHOLD 40    // Touch sensitivity

// MQTT
const char* mqtt_broker = "broker.emqx.io";
const int mqtt_port = 1883;
```

## 🐞 Troubleshooting

Common issues and solutions:

1. **Touch Sensitivity Issues**:
   - Adjust `THRESHOLD` value
   - Check touch sensor connection
   - Verify GPIO pin configuration

2. **Connection Problems**:
   - Verify WiFi credentials
   - Check MQTT broker accessibility
   - Ensure correct topic subscription

3. **Web Interface Issues**:
   - Clear browser cache
   - Check server logs
   - Verify WebSocket connection

## 📝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
