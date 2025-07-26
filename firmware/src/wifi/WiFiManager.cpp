#include "WiFiManager.h"

bool WiFiManager::begin() {
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    if (!connectToWiFi()) {
        return false;
    }
    
    if (!MDNS.begin(OTA_HOSTNAME)) {
        Serial.println("Error setting up MDNS responder!");
        return false;
    }
    
    Serial.printf("Connected to WiFi, IP: %s\n", getLocalIP().c_str());
    return true;
}

bool WiFiManager::connectToWiFi() {
    Serial.printf("Connecting to WiFi %s...\n", WIFI_SSID);
    
    unsigned long startAttemptTime = millis();
    
    while (WiFi.status() != WL_CONNECTED && 
           millis() - startAttemptTime < WIFI_TIMEOUT) {
        delay(100);
        Serial.print(".");
    }
    Serial.println();
    
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Failed to connect to WiFi");
        return false;
    }
    
    return true;
}

void WiFiManager::reconnect() {
    if (!isConnected()) {
        Serial.println("WiFi connection lost. Reconnecting...");
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        connectToWiFi();
    }
}
