#pragma once

#include "heltec.h"
#include "config.h"
#include <SPI.h>

class LoRaHandler {
public:
    static bool begin();
    static void sendAck(const char* state);
    static void send(const char* data);
    static int receive(uint8_t* buffer, size_t size);

private:
    static void configureModem();
};
