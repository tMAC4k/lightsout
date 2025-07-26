#pragma once

#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include "config.h"

class MQTTManager {
public:
    static bool begin();
    static void handle();
    static bool publish(const char* topic, const char* payload);
    static bool isConnected();

private:
    static void callback(char* topic, byte* payload, unsigned int length);
    static void reconnect();
    static PubSubClient client;
};
