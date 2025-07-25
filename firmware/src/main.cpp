#include <Arduino.h>
#include <heltec.h>
#include <Vector.h>
#include <string>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// Pin definitions
#define RELAY_PIN 21  // Example GPIO pin for relay control
#define LED_BUILTIN 25

// Task handles
TaskHandle_t loraTaskHandle;
TaskHandle_t lightControlTaskHandle;
TaskHandle_t menuTaskHandle;

// Message buffer
static QueueHandle_t msgQueue;

// Menu System
class MenuItem {
public:
    String title;
    String id;
    void (*callback)();
    
    MenuItem(String t, String i, void (*cb)()) : title(t), id(i), callback(cb) {}
};

class MenuSystem {
private:
    Vector<MenuItem*> items;
    int currentIndex = 0;
    bool needsRedraw = true;
    unsigned long lastInputTime = 0;
    const unsigned long inputDebounce = 200; // ms

public:
    MenuSystem() {
        items.setStorage(MenuItem*[10]); // Max 10 menu items
    }
    
    void addItem(String title, String id, void (*callback)()) {
        items.push_back(new MenuItem(title, id, callback));
    }
    
    void next() {
        if (millis() - lastInputTime < inputDebounce) return;
        currentIndex = (currentIndex + 1) % items.size();
        needsRedraw = true;
        lastInputTime = millis();
    }
    
    void select() {
        if (millis() - lastInputTime < inputDebounce) return;
        if (items[currentIndex]->callback) {
            items[currentIndex]->callback();
        }
        lastInputTime = millis();
    }
    
    void draw() {
        if (!needsRedraw) return;
        
        Heltec.display->clear();
        Heltec.display->setTextAlignment(TEXT_ALIGN_LEFT);
        Heltec.display->setFont(ArialMT_Plain_10);
        
        // Draw title
        Heltec.display->drawString(0, 0, "[LightsOut Node]");
        Heltec.display->drawHorizontalLine(0, 12, 128);
        
        // Draw menu items
        for (int i = 0; i < min(3, items.size()); i++) {
            int displayIndex = (currentIndex - 1 + i + items.size()) % items.size();
            String prefix = (i == 1) ? "> " : "  ";
            Heltec.display->drawString(0, 16 + i * 16, 
                prefix + items[displayIndex]->title);
        }
        
        // Draw status bar
        Heltec.display->drawHorizontalLine(0, 52, 128);
        Heltec.display->drawString(0, 54, "RF: 868MHz");
        
        Heltec.display->display();
        needsRedraw = false;
    }
};

// Global menu instance
MenuSystem menu;

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
