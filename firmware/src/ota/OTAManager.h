#pragma once

#include <ArduinoOTA.h>
#include "config.h"

class OTAManager {
public:
    static void begin();
    static void handle();
};
