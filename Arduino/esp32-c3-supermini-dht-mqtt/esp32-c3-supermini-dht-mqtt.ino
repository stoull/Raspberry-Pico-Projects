#include <WiFi.h>
#include <PubSubClient.h>
#include <DHTesp.h>

// WiFi
const char *ssid = "******"; // Enter your Wi-Fi name
const char *password = "******";  // Enter Wi-Fi password

// MQTT Broker
const char *mqtt_broker = "192.168.1.147";
const char *topic = "/fridge/temp-humidity";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// dht sensor
#define LED_PIN 8
int DHTPIN = 0;
DHTesp dhtSensor;

void setup() {
    // Set software serial baud to 115200;
    Serial.begin(115200);

    // setup dht sensor
    dhtSensor.setup(DHTPIN, DHTesp::DHT22);
    pinMode(LED_PIN, OUTPUT);

    // Connecting to a WiFi network
    WiFi.useStaticBuffers(true);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    WiFi.setTxPower(WIFI_POWER_8_5dBm);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to the Wi-Fi network");
    //connecting to a mqtt broker
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    while (!client.connected()) {
        String client_id = "esp32-client-";
        client_id += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());
        if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Public EMQX MQTT broker connected");
        } else {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }
    // Publish and subscribe
    // client.publish(topic, "{\"humidity\":60.0,\"temperature\":27.7}");
    // client.subscribe(topic);
}

// subscribe message call back
void callback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Message arrived in topic: ");
    Serial.println(topic);
    Serial.print("Message:");
    for (int i = 0; i < length; i++) {
        Serial.print((char) payload[i]);
    }
    Serial.println();
    Serial.println("-----------------------");
}

void loop() {
    // if subscribe any topic, start the blow line to run callback when received any message
    // client.loop();

    digitalWrite(LED_PIN, LOW);
    TempAndHumidity  data = dhtSensor.getTempAndHumidity();
    Serial.println(data.temperature);
    Serial.println(data.humidity);
    Serial.println("Temp: " + String(data.temperature, 2) + "°C");
    Serial.println("Humidity: " + String(data.humidity, 1) + "%");
    Serial.println("---");
    // char pub_msg[50];
    // snprintf(pub_msg, sizeof(pub_msg), "{\"humidity\":%s,\"temperature\":%s}", String(data.humidity, 1), String(data.temperature, 2));
    // Serial.println(pub_msg);
    String pub_msg=String("{\"humidity\":" + String(data.humidity, 1) + ",\"temperature\":" + String(data.temperature, 2) + "}");
    Serial.println(pub_msg);
    client.publish(topic, pub_msg.c_str());
    delay(3000);
    digitalWrite(LED_PIN, HIGH);
    delay(20000);
}
