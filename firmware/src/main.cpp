#include <Arduino.h>
#include <heltec.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// Pin definitions
#define RELAY_PIN 21  // Example GPIO pin for relay control
#define LED_BUILTIN 25

// Task handles
TaskHandle_t loraTaskHandle;
TaskHandle_t lightControlTaskHandle;

// Message buffer
static QueueHandle_t msgQueue;

// Function prototypes
void loraTask(void *pvParameters);
void lightControlTask(void *pvParameters);

void setup() {
    // Initialize Heltec WiFi LoRa 32
    Heltec.begin(true /*DisplayEnable Enable*/, true /*LoRa Enable*/, true /*Serial Enable*/, true /*LoRa use PABOOST*/, 868E6 /*LoRa RF working band*/);
    
    // Initialize GPIO
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    
    // Create message queue
    msgQueue = xQueueCreate(10, sizeof(uint8_t));
    
    // Create tasks
    xTaskCreate(
        loraTask,           // Task function
        "LoRaTask",        // Name for debugging
        10000,             // Stack size (bytes)
        NULL,              // Parameters
        1,                 // Priority
        &loraTaskHandle    // Task handle
    );
    
    xTaskCreate(
        lightControlTask,
        "LightControl",
        10000,
        NULL,
        1,
        &lightControlTaskHandle
    );
}

void loop() {
    // Empty loop - tasks handle everything
    vTaskDelay(pdMS_TO_TICKS(1000));
}

void loraTask(void *pvParameters) {
    uint8_t packet[255];
    
    while (1) {
        // Check if packet received
        int packetSize = LoRa.parsePacket();
        if (packetSize) {
            // Read packet
            int i = 0;
            while (LoRa.available()) {
                packet[i++] = LoRa.read();
            }
            
            // Process command (simple example)
            if (i > 0) {
                xQueueSend(msgQueue, &packet[0], portMAX_DELAY);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void lightControlTask(void *pvParameters) {
    uint8_t command;
    
    while (1) {
        if (xQueueReceive(msgQueue, &command, portMAX_DELAY) == pdTRUE) {
            switch (command) {
                case '1':  // Turn on
                    digitalWrite(RELAY_PIN, HIGH);
                    digitalWrite(LED_BUILTIN, HIGH);
                    // Send acknowledgment
                    LoRa.beginPacket();
                    LoRa.print("ACK:ON");
                    LoRa.endPacket();
                    break;
                    
                case '0':  // Turn off
                    digitalWrite(RELAY_PIN, LOW);
                    digitalWrite(LED_BUILTIN, LOW);
                    // Send acknowledgment
                    LoRa.beginPacket();
                    LoRa.print("ACK:OFF");
                    LoRa.endPacket();
                    break;
            }
        }
    }
}
