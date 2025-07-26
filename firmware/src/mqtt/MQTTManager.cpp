#include "MQTTManager.h"
#include "../tasks/TaskManager.h"

WiFiClient espClient;
PubSubClient MQTTManager::client(espClient);

bool MQTTManager::begin() {
    client.setServer(MQTT_BROKER, MQTT_PORT);
    client.setCallback(callback);
    return true;
}

void MQTTManager::callback(char* topic, byte* payload, unsigned int length) {
    // Convert payload to null-terminated string
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    
    if (strcmp(topic, MQTT_TOPIC_COMMAND) == 0) {
        // Forward command to task queue
        if (length > 0) {
            xQueueSend(TaskManager::getMessageQueue(), &payload[0], portMAX_DELAY);
        }
    }
}

void MQTTManager::reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        if (client.connect(MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)) {
            Serial.println("connected");
            client.subscribe(MQTT_TOPIC_COMMAND);
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 5 seconds");
            delay(5000);
        }
    }
}

void MQTTManager::handle() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}

bool MQTTManager::publish(const char* topic, const char* payload) {
    if (!client.connected()) {
        return false;
    }
    return client.publish(topic, payload);
}

bool MQTTManager::isConnected() {
    return client.connected();
}
