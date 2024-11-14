#include <WiFi.h>
#include <PubSubClient.h>

// WiFi settings - Replace with your WiFi credentials
const char* ssid = "charon";
const char* password = "12121212";

// MQTT settings
const char* mqtt_broker = "broker.emqx.io";
const int mqtt_port = 1883;
const char* topic_touch_state = "esmail/touch_state";

// Pin definitions
#define TOUCH_PIN T0    // GPIO4 - Touch sensor pin
#define LED_PIN 2       // GPIO2 - Built-in LED
#define THRESHOLD 40    // Touch sensitivity threshold

// Global variables
String device_id;       // Unique device identifier
WiFiClient espClient;   // WiFi client instance
PubSubClient client(espClient);  // MQTT client instance

// Setup WiFi connection
void setup_wifi() {
    Serial.println("Connecting to WiFi...");
    WiFi.mode(WIFI_STA);  // Set WiFi to station mode
    WiFi.begin(ssid, password);

    // Wait for connection
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

// MQTT message callback
void callback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Message arrived on topic [");
    Serial.print(topic);
    Serial.print("]: ");
    Serial.println(message);
    
    // Parse message (format: "deviceId:state")
    int separator = message.indexOf(':');
    if (separator != -1) {
        String sender_id = message.substring(0, separator);
        String touch_state = message.substring(separator + 1);
        
        // Only respond to messages from other devices
        if (sender_id != device_id) {
            if (touch_state == "1") {
                digitalWrite(LED_PIN, HIGH);
                Serial.println("LED ON - Command from: " + sender_id);
            } else {
                digitalWrite(LED_PIN, LOW);
                Serial.println("LED OFF - Command from: " + sender_id);
            }
        }
    }
}

// Reconnect to MQTT broker
void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        // Create a random client ID
        String client_id = "esp32-client-";
        client_id += String(random(0xffff), HEX);
        
        // Attempt to connect
        if (client.connect(client_id.c_str())) {
            Serial.println("connected");
            
            // Subscribe to touch state topic
            client.subscribe(topic_touch_state);
            
            // Send initial state
            String message = device_id + ":0";
            client.publish(topic_touch_state, message.c_str());
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 5 seconds");
            delay(5000);
        }
    }
}

void setup() {
    // Initialize serial communication
    Serial.begin(115200);
    while (!Serial) delay(100);
    Serial.println("\nESP32 MQTT Touch Sensor Start");
    
    // Configure pins
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    // Configure touch sensor
    touchSetCycles(0x1000, 0x1000);  // Configure touch sensor sensitivity
    
    // Generate unique device ID using ESP32's MAC address
    device_id = "ESP32_" + String((uint32_t)ESP.getEfuseMac(), HEX);
    Serial.print("Device ID: ");
    Serial.println(device_id);
    
    // Setup WiFi and MQTT
    setup_wifi();
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    
    Serial.println("Setup complete");
}

void loop() {
    // Ensure MQTT connection
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
    
    // Read touch sensor
    uint16_t touchValue = touchRead(TOUCH_PIN);
    static bool lastTouchState = false;
    bool currentTouchState = touchValue < THRESHOLD;
    
    // Debug touch values
    static unsigned long lastDebugTime = 0;
    if (millis() - lastDebugTime > 1000) {  // Print debug info every second
        Serial.printf("Touch value: %d, Threshold: %d\n", touchValue, THRESHOLD);
        lastDebugTime = millis();
    }
    
    // Check for touch state change
    if (currentTouchState != lastTouchState) {
        // Format message as "deviceId:state"
        String message = device_id + ":" + (currentTouchState ? "1" : "0");
        
        Serial.print("Touch state changed: ");
        Serial.println(currentTouchState ? "TOUCHED" : "RELEASED");
        Serial.print("Publishing message: ");
        Serial.println(message);
        
        // Publish message to MQTT broker
        if (client.publish(topic_touch_state, message.c_str())) {
            Serial.println("Message published successfully");
        } else {
            Serial.println("Failed to publish message");
        }
        
        // Update last state
        lastTouchState = currentTouchState;
    }
    
    // Small delay to prevent too frequent readings
    delay(100);
}
