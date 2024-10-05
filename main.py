"""
A simple example that connects to the Adafruit IO MQTT server
and publishes values that represent a sine wave
"""

import network
import time
import json
from math import sin
from umqtt.simple import MQTTClient

from machine import Pin
from dht_sensor import readDHT
led_pin = Pin("LED", Pin.OUT)

wifi_ssid = "******"
wifi_password = "******"

# 日志相关
log_file = open("_log.txt", "w")
startTime_str = "the start time：%s" %str(time.localtime())
log_file.write(startTime_str + "\n")
log_file.flush()

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.config(pm=network.WLAN.PM_NONE)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

led_pin.on()

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
        if isinstance(temp_hum, OSError):
            log_str = "e1：%s" %str(temp_hum)
            log_file.write(log_str + "\n")
            log_file.flush()
        elif temp_hum is not None:
            try:
                info = {
                    "temperature": temp_hum[0],
                    "humidity": temp_hum[1],
                    }
                info_s = json.dumps(info)
                # print('"temperature":{} '.format(info_s))
                log_str = "t：%s" %str(time.localtime())
                log_file.write(log_str + "\n")
                log_file.flush()
                mqtt_client.publish(mqtt_publish_topic, info_s)
            except Exception as e:
                log_str = "e2：%s" %str(e)
                log_file.write(log_str + "\n")
                log_file.flush()
        else:
            # print('the value is none')
            pass
        
        # Delay a bit to avoid hitting the rate limit
        time.sleep(120)
except Exception as e:
    log_str = "e4：%s" %str(e)
    log_file.write(log_str + "\n")
    log_file.flush()
    # print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()
    log_file.write("disconnected mqtt")
    log_file.flush()


