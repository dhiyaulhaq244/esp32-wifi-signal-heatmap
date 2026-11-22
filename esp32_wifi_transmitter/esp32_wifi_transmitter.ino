/*
  ESP32 Wi-Fi Transmitter for Signal Mapping
  Role: ESP32 SoftAP (transmitter), laptop is the receiver.
  Board: ESP32 Dev Module
*/

#include <WiFi.h>

const char* AP_SSID = "ESP32_WIFI_TX";
const char* AP_PASSWORD = "wifiheatmap";  // Minimum 8 characters
const int AP_CHANNEL = 6;
const int MAX_CONNECTIONS = 4;

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_AP);

  // Start the ESP32 as a 2.4 GHz Wi-Fi access point.
  bool started = WiFi.softAP(
    AP_SSID,
    AP_PASSWORD,
    AP_CHANNEL,
    false,
    MAX_CONNECTIONS
  );

  if (started) {
    Serial.println();
    Serial.println("ESP32 Wi-Fi transmitter started.");
    Serial.print("SSID: ");
    Serial.println(AP_SSID);
    Serial.print("Channel: ");
    Serial.println(AP_CHANNEL);
    Serial.print("AP IP address: ");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.println("ERROR: Failed to start ESP32 SoftAP.");
  }
}

void loop() {
  // Keep the access point active and report connected clients.
  static unsigned long lastReport = 0;

  if (millis() - lastReport >= 5000) {
    lastReport = millis();
    Serial.print("Connected station(s): ");
    Serial.println(WiFi.softAPgetStationNum());
  }

  delay(10);
}
