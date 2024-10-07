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

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "192.168.31.11"
mqtt_port = 1883
mqtt_publish_topic = "/fridge/temp-humidity"  # The MQTT topic for your Adafruit IO Feed

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "WCwsVCBZa1xcSlRTUzwsaXkiUXlwOVVgKg"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.config(pm=network.WLAN.PM_NONE)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    log_file.write("Waiting for connection...\n")
    time.sleep(1)
print("Connected to WiFi")
log_file.write("Connected to WiFi\n")

led_pin.on()

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        port=mqtt_port)
mqtt_client.connect()
log_file.write("Connected to MQTT\n")

def startLooping():
    log_file.write("startLooping\n")
    try:
        while True:
            log_file.write("start readDHT\n")
            temp_hum = readDHT()
            log_file.write(str(type(temp_hum)))
            log_file.write(" end readDHT\n")
            if isinstance(temp_hum, Exception):
                log_str = "e1：%s" %str(temp_hum)
                log_file.write(log_str + "\n")
                log_file.flush()
            elif temp_hum is not None:
                info = {
                    "temperature": temp_hum[0],
                    "humidity": temp_hum[1],
                    }
                info_s = json.dumps(info)
                # print('"temperature":{} '.format(info_s))
                log_file.flush()
                mqtt_client.publish(mqtt_publish_topic, info_s)
            else:
                # print('the value is none')
                pass
            
            # Delay a bit to avoid hitting the rate limit
            time.sleep(120)
            #for x in range(0, 12):
            #   time.sleep(10)
            #   mqtt_client.ping()
                
    except SystemExit as e:
        log_file.write("SystemExit\n")
    except KeyboardInterrupt as e:
        log_file.write("KeyboardInterrupt\n")
    except GeneratorExit as e:
        log_file.write("GeneratorExit\n")
    except Exception as e:
        log_str2 = "e4：%s" %str(e)
        log_file.write(type(e) + "\n")
        log_file.write(log_str2 + "\n")
        log_file.flush()
        # print(f'Failed to publish message: {e}')
    finally:
        mqtt_client.disconnect()
        log_file.write("mqtt disconnected\n")
        log_file.flush()
        time.sleep(30)
        startLooping()
        # machine.reset()
        
startLooping()

