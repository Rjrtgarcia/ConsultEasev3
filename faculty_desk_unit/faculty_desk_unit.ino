/*
  ConsultEase - Faculty Desk Unit

  This firmware runs on an ESP32 and provides a faculty desk interface for the ConsultEase system.
  It displays consultation requests and updates faculty presence status using BLE.

  Hardware:
  - ESP32 development board
  - SSD1306 OLED display (128x64)
  - Optional buttons for interaction
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <vector>
#include <string>
#include <Preferences.h>

// Configuration
// Update these values with your actual WiFi and MQTT details
const char* ssid = "YourWiFiSSID";         // WiFi SSID
const char* password = "YourWiFiPassword";  // WiFi password
const char* mqtt_server = "192.168.1.100";  // MQTT broker address
const int mqtt_port = 1883;                 // MQTT broker port
const char* faculty_id = "faculty001";      // Faculty ID (must match database)
const char* faculty_name = "Dr. Smith";     // Faculty name
const char* department = "Computer Science"; // Department
const char* ble_beacon_id = "AA:BB:CC:DD:EE:01"; // BLE beacon MAC address

// Display configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

// Button pins (optional)
#define BUTTON_ACK 12    // Acknowledge button
#define BUTTON_BUSY 14   // Busy/Available toggle button
#define BUTTON_COMPLETE 27 // Complete request button

// BLE scanning parameters
#define SCAN_INTERVAL 15000      // BLE scan interval in milliseconds
#define PRESENCE_TIMEOUT 30000   // Time before marking faculty as unavailable

// MQTT topics
String status_topic;
String requests_topic;
String notifications_topic;

// Global variables
WiFiClient espClient;
PubSubClient mqtt_client(espClient);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
BLEScan* ble_scan;
unsigned long last_scan_time = 0;
unsigned long last_beacon_time = 0;
bool faculty_present = false;
String current_status = "unavailable";
bool wifi_connected = false;
bool mqtt_connected = false;
unsigned long last_reconnect_attempt = 0;
const unsigned long RECONNECT_INTERVAL = 5000; // 5 seconds between reconnection attempts
Preferences preferences; // For persistent storage

// Button debounce variables
unsigned long last_button_time = 0;
const unsigned long DEBOUNCE_DELAY = 200; // milliseconds

// Consultation requests
struct ConsultationRequest {
  String id;
  String student_id;
  String student_name;
  String request_text;
  String timestamp;
  String status;
};

std::vector<ConsultationRequest> requests;
int current_request_index = 0;

// Function prototypes
void setup_wifi();
bool reconnect_mqtt();
void mqtt_callback(char* topic, byte* payload, unsigned int length);
void scan_for_beacon();
void update_display();
void publish_status();
void handle_buttons();
void save_settings();
void load_settings();

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    // Check if this is our beacon
    if (advertisedDevice.getAddress().toString() == ble_beacon_id) {
      Serial.println("Found faculty beacon!");
      last_beacon_time = millis();
      
      // Update faculty presence if needed
      if (!faculty_present) {
        faculty_present = true;
        
        // Only change status to available if not manually set to busy
        if (current_status != "busy") {
          current_status = "available";
          publish_status();
        }
        
        update_display();
      }
    }
  }
};

void setup() {
  Serial.begin(115200);
  Serial.println("ConsultEase Faculty Desk Unit");
  
  // Initialize preferences for persistent storage
  preferences.begin("consultease", false);
  
  // Load saved settings
  load_settings();
  
  // Initialize display
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("ConsultEase");
  display.println("Faculty Desk Unit");
  display.println("Initializing...");
  display.println(faculty_name);
  display.println(department);
  display.display();
  
  // Setup button pins
  pinMode(BUTTON_ACK, INPUT_PULLUP);
  pinMode(BUTTON_BUSY, INPUT_PULLUP);
  pinMode(BUTTON_COMPLETE, INPUT_PULLUP);
  
  // Setup MQTT topics
  status_topic = String("faculty/") + faculty_id + "/status";
  requests_topic = String("faculty/") + faculty_id + "/requests";
  notifications_topic = "consultease/notifications";
  
  // Setup WiFi
  setup_wifi();
  
  // Setup MQTT
  mqtt_client.setServer(mqtt_server, mqtt_port);
  mqtt_client.setCallback(mqtt_callback);
  
  // Setup BLE scanning
  BLEDevice::init("ConsultEase Faculty Unit");
  ble_scan = BLEDevice::getScan();
  ble_scan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  ble_scan->setActiveScan(true);
  ble_scan->setInterval(100);
  ble_scan->setWindow(99);
  
  // Initial display update
  update_display();
}

void loop() {
  unsigned long current_time = millis();
  
  // Ensure WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    wifi_connected = false;
    
    // Only attempt reconnection every RECONNECT_INTERVAL
    if (current_time - last_reconnect_attempt > RECONNECT_INTERVAL) {
      last_reconnect_attempt = current_time;
    setup_wifi();
    }
  } else {
    wifi_connected = true;
  }
  
  // Ensure MQTT connection if WiFi is connected
  if (wifi_connected && !mqtt_client.connected()) {
    mqtt_connected = false;
    
    // Only attempt reconnection every RECONNECT_INTERVAL
    if (current_time - last_reconnect_attempt > RECONNECT_INTERVAL) {
      last_reconnect_attempt = current_time;
    reconnect_mqtt();
    }
  } else if (wifi_connected) {
    mqtt_connected = true;
    mqtt_client.loop();
  }
  
  // Perform BLE scanning at intervals
  if (current_time - last_scan_time > SCAN_INTERVAL) {
    scan_for_beacon();
    last_scan_time = current_time;
  }
  
  // Check for faculty presence timeout
  if (faculty_present && (current_time - last_beacon_time > PRESENCE_TIMEOUT)) {
    faculty_present = false;
    
    // Only update status if not manually set to busy
    if (current_status != "busy") {
    current_status = "unavailable";
    publish_status();
    }
    
    update_display();
  }
  
  // Handle button presses
  handle_buttons();
  
  // Other periodic tasks
  delay(100);
}

void load_settings() {
  // Load any persistent settings
  if (preferences.isKey("status")) {
    current_status = preferences.getString("status", "unavailable");
    Serial.println("Loaded saved status: " + current_status);
  }
}

void save_settings() {
  // Save settings to persistent storage
  preferences.putString("status", current_status);
  Serial.println("Saved status: " + current_status);
}

void setup_wifi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  // Use static IP if needed
  // WiFi.config(IPAddress(192, 168, 1, 200), IPAddress(192, 168, 1, 1), IPAddress(255, 255, 255, 0));
  
  WiFi.begin(ssid, password);
  
  // Wait up to 20 seconds for connection
  int timeout = 0;
  while (WiFi.status() != WL_CONNECTED && timeout < 200) {
    delay(100);
    timeout++;
    Serial.print(".");
    
    if (timeout % 10 == 0) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("Connecting to WiFi...");
      display.println(ssid);
      display.println("Attempt: " + String(timeout / 10));
      display.display();
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    
    wifi_connected = true;
    
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("WiFi connected");
    display.println(WiFi.localIP().toString());
    display.display();
    delay(1000);
  } else {
    Serial.println("WiFi connection failed");
    wifi_connected = false;
    
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("WiFi connection failed");
    display.println("Will retry...");
    display.display();
  }
}

bool reconnect_mqtt() {
  if (!wifi_connected) {
    return false;
  }
  
  Serial.print("Attempting MQTT connection...");
  
  // Create a client ID
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);
  
  // Attempt to connect
  if (mqtt_client.connect(clientId.c_str())) {
    Serial.println("connected");
    mqtt_connected = true;
    
    // Subscribe to topics
    mqtt_client.subscribe(requests_topic.c_str());
    
    // Publish current status upon reconnection
    publish_status();
    
    return true;
  } else {
    Serial.print("failed, rc=");
    Serial.print(mqtt_client.state());
    Serial.println(" will try again");
    mqtt_connected = false;
    
    return false;
  }
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convert payload to string
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Handle message based on topic
  if (String(topic) == requests_topic) {
    // Parse JSON
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }
  
    // Process the consultation request
    ConsultationRequest request;
    request.id = doc["id"].as<String>();
    request.student_id = doc["student_id"].as<String>();
    request.student_name = doc["student_name"].as<String>();
    request.request_text = doc["request_text"].as<String>();
    request.timestamp = doc["timestamp"].as<String>();
    request.status = doc["status"].as<String>();
    
    // Check if request already exists
    bool exists = false;
    for (unsigned int i = 0; i < requests.size(); i++) {
      if (requests[i].id == request.id) {
        // Update existing request
        requests[i] = request;
        exists = true;
        break;
      }
    }
    
    // Add new request if it doesn't exist
    if (!exists) {
    requests.push_back(request);
      
      // Automatically set current request to the newest one
      current_request_index = requests.size() - 1;
    }
    
    // Update display
    update_display();
  }
}

void scan_for_beacon() {
  if (!BLEDevice::getInitialized()) {
    Serial.println("BLE not initialized");
    return;
  }
  
  Serial.println("Scanning for BLE devices...");
  BLEScanResults foundDevices = ble_scan->start(3, false); // Scan for 3 seconds
  Serial.print("Devices found: ");
  Serial.println(foundDevices.getCount());
  ble_scan->clearResults();
}

void publish_status() {
  if (!mqtt_connected) {
    return;
  }
  
  // Create JSON document
  DynamicJsonDocument doc(256);
  doc["faculty_id"] = faculty_id;
  doc["status"] = current_status;
  doc["department"] = department;
  doc["timestamp"] = String(millis());
  
  // Serialize to JSON
  String message;
  serializeJson(doc, message);
  
  // Publish status
  mqtt_client.publish(status_topic.c_str(), message.c_str(), true);
  Serial.println("Published status: " + message);
  
  // Save current status to persistent storage
  save_settings();
}

void handle_buttons() {
  unsigned long current_time = millis();
  
  // Debounce check
  if (current_time - last_button_time < DEBOUNCE_DELAY) {
    return;
  }
  
  // Acknowledge button - cycle through requests
  if (digitalRead(BUTTON_ACK) == LOW) {
    last_button_time = current_time;
    
      if (requests.size() > 0) {
        current_request_index = (current_request_index + 1) % requests.size();
        update_display();
    }
  }
  
  // Busy/Available toggle button
  if (digitalRead(BUTTON_BUSY) == LOW) {
    last_button_time = current_time;
    
      if (current_status == "available") {
      current_status = "busy";
    } else if (current_status == "busy") {
      current_status = "available";
    } else if (current_status == "unavailable" && faculty_present) {
        current_status = "available";
      }
      
      publish_status();
      update_display();
  }
  
  // Complete request button
  if (digitalRead(BUTTON_COMPLETE) == LOW) {
    last_button_time = current_time;
    
      if (requests.size() > 0) {
      // Mark current request as completed
      String request_id = requests[current_request_index].id;
      
      if (mqtt_connected) {
        // Create JSON document
        DynamicJsonDocument doc(256);
        doc["faculty_id"] = faculty_id;
        doc["request_id"] = request_id;
        doc["status"] = "completed";
        doc["timestamp"] = String(millis());
        
        // Serialize to JSON
        String message;
        serializeJson(doc, message);
        
        // Publish complete notification
        mqtt_client.publish(notifications_topic.c_str(), message.c_str());
        Serial.println("Published completion: " + message);
      }
      
      // Remove completed request from the list
      requests.erase(requests.begin() + current_request_index);
        
      // Update current index
      if (requests.size() > 0) {
        current_request_index = current_request_index % requests.size();
      } else {
          current_request_index = 0;
        }
        
        update_display();
      }
  }
}

void update_display() {
  display.clearDisplay();
  display.setCursor(0, 0);
  
  // Show faculty info
  display.setTextSize(1);
  display.println(faculty_name);
  display.println(department);
  
  // Show status
  display.setTextSize(1);
  display.print("Status: ");
  if (current_status == "available") {
    display.println("AVAILABLE");
  } else if (current_status == "busy") {
    display.println("BUSY");
  } else {
    display.println("UNAVAILABLE");
  }
  
  // Show connection status
  display.print("WiFi: ");
  display.print(wifi_connected ? "OK" : "X");
  display.print(" MQTT: ");
  display.println(mqtt_connected ? "OK" : "X");
  
  // Show requests
  display.println("-------------------");
  
  if (requests.size() > 0) {
    ConsultationRequest& request = requests[current_request_index];
    
    display.print("Request ");
    display.print(current_request_index + 1);
    display.print("/");
    display.println(requests.size());
    
    display.print("From: ");
    display.println(request.student_name);
    
    display.println(request.request_text.substring(0, 20));
    if (request.request_text.length() > 20) {
      display.println(request.request_text.substring(20, 40));
      }
  } else {
    display.println("No pending requests");
  }
  
  display.display();
}
