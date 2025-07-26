#pragma once

// Pin definitions for Heltec WiFi LoRa 32 V3
#define RELAY_PIN 21
#define STATUS_LED 35  // Built-in LED on GPIO35 for Heltec WiFi LoRa 32 V3

// LoRa Configuration for Heltec WiFi LoRa 32 V3
#define LORA_BAND        868E6  // Hz
#define LORA_SF         7      // Spreading Factor
#define LORA_BW         125E3  // Bandwidth
#define LORA_CR         5      // Coding Rate
#define LORA_SYNCWORD   0x12   // Sync Word
#define LORA_TXPOWER    14     // dBm
#define LORA_SCK        5      // GPIO5  - SX1276 SCK
#define LORA_MISO       2      // GPIO2  - SX1276 MISO
#define LORA_MOSI       4      // GPIO4  - SX1276 MOSI
#define LORA_SS         9     // GPIO9  - SX1276 CS
#define LORA_RST        13     // GPIO13 - SX1276 RST
#define LORA_DI0        14     // GPIO14 - SX1276 IRQ(DIO0)

// Task Configuration
#define STACK_SIZE 10000
#define TASK_PRIORITY 1
#define QUEUE_SIZE 10

// Display Configuration
#define DISPLAY_ENABLED true
