#pragma once

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>

class TaskManager {
public:
    static bool begin();
    static QueueHandle_t getMessageQueue() { return msgQueue; }
    
private:
    static void loraTask(void* pvParameters);
    static void lightControlTask(void* pvParameters);
    
    static QueueHandle_t msgQueue;
    static TaskHandle_t loraTaskHandle;
    static TaskHandle_t lightControlTaskHandle;
};
