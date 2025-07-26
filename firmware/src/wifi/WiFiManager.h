#pragma once

#include <WiFi.h>
#include <ESPmDNS.h>
#include "config.h"

class WiFiManager {
public:
    static bool begin();
    static bool isConnected() { return WiFi.isConnected(); }
    static void reconnect();
    static String getLocalIP() { return WiFi.localIP().toString(); }

private:
    static bool connectToWiFi();
};
