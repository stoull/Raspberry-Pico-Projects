"""
A simple example that connects to the Adafruit IO MQTT server
and publishes values that represent a sine wave
"""

import network
import time
import json
from math import sin
from umqtt.simple import MQTTClient

from dht_sensor import readDHT

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = "******"
wifi_password = "******"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.config(pm=network.WLAN.PM_NONE)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "192.168.31.11"
mqtt_port = 1883
mqtt_publish_topic = "/fridge/temp-humidity"  # The MQTT topic for your Adafruit IO Feed

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "WCwsVCBZa1xcSlRTUzwsaXkiUXlwOVVgKg"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        port=mqtt_port)

mqtt_client.connect()


counter = 0
try:
    while True:
        temp_hum = readDHT()
        if temp_hum is not None:
            info = {
                "temperature": temp_hum[0],
                "humidity": temp_hum[1],
                }
            info_s = json.dumps(info)
            # print('"temperature":{} '.format(info_s))
            
            mqtt_client.publish(mqtt_publish_topic, info_s)
        else:
            # print('the value is none')
            pass
        
        # Delay a bit to avoid hitting the rate limit
        time.sleep(120)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()
