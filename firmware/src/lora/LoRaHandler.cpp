#include "LoRaHandler.h"
// Add mutex for thread safety
static SemaphoreHandle_t loraMutex = NULL;

bool LoRaHandler::begin() {
    if (loraMutex == NULL) {
        loraMutex = xSemaphoreCreateMutex();
        if (loraMutex == NULL) return false;
    }

    // Initialize SPI for LoRa
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    
    // Initialize Heltec board with display and serial
    Heltec.begin(DISPLAY_ENABLED /*DisplayEnable*/,
                 false /*LoRa Disable - we'll initialize it manually*/,
                 true /*Serial Enable*/,
                 true /*PABOOST Enable*/,
                 LORA_BAND /*Band*/);
                 
    // Configure LoRa pins
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DI0);
    
    // Try to initialize LoRa with PABOOST enabled
    if (!LoRa.begin(LORA_BAND, true)) {
        Serial.println("Starting LoRa failed!");
        return false;
    }
    
    configureModem();
    return true;
}

void LoRaHandler::configureModem() {
    LoRa.setSpreadingFactor(LORA_SF);
    LoRa.setSignalBandwidth(LORA_BW);
    LoRa.setCodingRate4(LORA_CR);
    LoRa.setPreambleLength(8);
    LoRa.setSyncWord(LORA_SYNCWORD);
    LoRa.setTxPower(LORA_TXPOWER, RF_PACONFIG_PASELECT_PABOOST);
    LoRa.enableCrc();
}

void LoRaHandler::sendAck(const char* state) {
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "ACK:%s", state);
    send(buffer);
}

void LoRaHandler::send(const char* data) {
    if (xSemaphoreTake(loraMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        LoRa.beginPacket();
        LoRa.print(data);
        LoRa.endPacket();
        xSemaphoreGive(loraMutex);
    }
}

int LoRaHandler::receive(uint8_t* buffer, size_t size) {
    int packetSize = LoRa.parsePacket();
    if (!packetSize) return 0;

    int i = 0;
    while (LoRa.available() && i < size - 1) {
        buffer[i++] = LoRa.read();
    }
    buffer[i] = 0; // Null terminate
    return i;
}
