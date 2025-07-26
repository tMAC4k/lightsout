#include "Arduino.h"
#include "config.h"
#include "lora/LoRaHandler.h"
#include "tasks/TaskManager.h"

void setup() {
    Serial.begin(115200);
    delay(300);
    
    Serial.println("Starting LightsOut Node...");
    
    if (!LoRaHandler::begin()) {
        Serial.println("LoRa initialization failed!");
        while (1) { delay(100); }
    }
    Serial.println("LoRa initialized!");
    
    if (!TaskManager::begin()) {
        Serial.println("Task initialization failed!");
        while (1) { delay(100); }
    }
    Serial.println("Tasks initialized!");
    
    Serial.println("Setup complete!");
}
void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
