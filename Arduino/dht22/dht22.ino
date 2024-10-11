  #include "DHTesp.h"
  #define LED_PIN 8

  int DHTPIN = 0;
  DHTesp dhtSensor;


  void setup() {
    Serial.begin(115200);
    Serial.println();
    Serial.println("Reset");
    Serial.println();
    dhtSensor.setup(DHTPIN, DHTesp::DHT22);
    pinMode(LED_PIN, OUTPUT);
  }

  void loop() {
    digitalWrite(LED_PIN, LOW);
    TempAndHumidity  data = dhtSensor.getTempAndHumidity();
    Serial.println("Temp: " + String(data.temperature, 2) + "°C");
    Serial.println("Humidity: " + String(data.humidity, 1) + "%");
    Serial.println("---");
    delay(3000);
    digitalWrite(LED_PIN, HIGH);
    delay(20000);
  }
