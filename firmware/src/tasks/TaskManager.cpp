#include "TaskManager.h"
#include "config.h"
#include "../lora/LoRaHandler.h"
#include "../mqtt/MQTTManager.h"
#include <Arduino.h>

QueueHandle_t TaskManager::msgQueue = NULL;
TaskHandle_t TaskManager::loraTaskHandle = NULL;
TaskHandle_t TaskManager::lightControlTaskHandle = NULL;

// Define a proper message structure
typedef struct {
    uint8_t command;
    char payload[32];
} lora_message_t;

bool TaskManager::begin() {
    // Create message queue
    msgQueue = xQueueCreate(QUEUE_SIZE, sizeof(uint8_t));
    if (msgQueue == NULL) {
        Serial.println("Failed to create message queue!");
        return false;
    }
    
    // Create tasks
    BaseType_t result;
    
    result = xTaskCreate(loraTask,
                        "LoRaTask",
                        STACK_SIZE,
                        NULL,
                        TASK_PRIORITY,
                        &loraTaskHandle);
    if (result != pdPASS) {
        Serial.println("Failed to create LoRa task!");
        return false;
    }
    
    result = xTaskCreate(lightControlTask,
                        "LightControl",
                        STACK_SIZE,
                        NULL,
                        TASK_PRIORITY,
                        &lightControlTaskHandle);
    if (result != pdPASS) {
        Serial.println("Failed to create Light Control task!");
        return false;
    }
    
    return true;
}

void TaskManager::loraTask(void* pvParameters) {
    static uint8_t packet[255];
    
    Serial.println("LoRa Task Started");
    
    for(;;) {
        int received = LoRaHandler::receive(packet, sizeof(packet));
        if (received > 0) {
            Serial.printf("Received: %s\n", packet);
            xQueueSend(msgQueue, &packet[0], portMAX_DELAY);
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void TaskManager::lightControlTask(void* pvParameters) {
    uint8_t command;
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(STATUS_LED, OUTPUT);
    
    for(;;) {
        if (xQueueReceive(msgQueue, &command, portMAX_DELAY) == pdTRUE) {
            switch (command) {
                case '1':  // Turn on
                    digitalWrite(RELAY_PIN, HIGH);
                    digitalWrite(STATUS_LED, HIGH);
                    LoRaHandler::sendAck("ON");
                    MQTTManager::publish(MQTT_TOPIC_STATE, "ON");
                    Serial.println("Light ON");
                    Serial.println("Light ON");
                    break;
                    
                case '0':  // Turn off
                    digitalWrite(RELAY_PIN, LOW);
                    digitalWrite(STATUS_LED, LOW);
                    LoRaHandler::sendAck("OFF");
                    MQTTManager::publish(MQTT_TOPIC_STATE, "OFF");
                    Serial.println("Light OFF");
                    Serial.println("Light OFF");
                    break;
            }
        }
    }
}
