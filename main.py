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
mqtt_host = "192.168.1.157"
mqtt_port = 1883
mqtt_publish_topic = "sensor/dht22/2/data"  # The MQTT topic for your Adafruit IO Feed
mqtt_user = b"******"
mqtt_password = b"******"

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "WCwsVCBZa1xcSlRTUzwsaXkiUXlwOVVgKg"

def currentDate_ISO8601():
    # 方法1：获取当前时间戳并转换为时间元组
    current_time = time.localtime()
    # 格式化为 ISO 8601 格式 (YYYY-MM-DDTHH:MM:SS)
    iso8601_time = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        current_time[0],  # 年
        current_time[1],  # 月
        current_time[2],  # 日
        current_time[3],  # 时
        current_time[4],  # 分
        current_time[5]   # 秒
    )

    # print(iso8601_time)
    # 输出示例: 2025-12-10T14:30:45
    return iso8601_time

def startLooping():
    log_file.write("startLooping\n")
    try:
        # Initialize our MQTTClient and connect to the MQTT server
        mqtt_client = MQTTClient(
                client_id=mqtt_client_id,
                server=mqtt_host,
                port=mqtt_port,
                user=mqtt_user,
                password=mqtt_password
                )
        mqtt_client.connect()
        while True:
            temp_hum = readDHT()
            if isinstance(temp_hum, OSError):
                log_str = "e1：%s" %str(temp_hum)
                log_file.write(log_str + "\n")
                log_file.flush()
            elif temp_hum is not None:
                try:
                    c_date = currentDate_ISO8601()
                    info = {
                        "created_at": c_date,
                        "temperature": temp_hum[0],
                        "humidity": temp_hum[1],
                        }
                    info_s = json.dumps(info)
                    # print('"temperature":{} '.format(info_s))
                    # log_str = "t：%s" %str(time.localtime())
                    # log_file.write(log_str + "\n")
                    # log_file.write(info_s + "\n")
                    # log_file.flush()
                    mqtt_client.publish(mqtt_publish_topic, info_s)
                except Exception as e:
                    log_str = "e2：%s" %str(e)
                    log_file.write(log_str + "\n")
                    log_file.flush()
            else:
                # print('the value is none')
                pass
            
            # Delay a bit to avoid hitting the rate limit
            log_file.write("before sleep\n")
            log_file.flush()
            time.sleep(300)
            log_file.write("after sleep\n")
            log_file.flush()
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
        log_file.write("disconnected mqtt\n")
        log_file.flush()
        time.sleep(6)
        startLooping()
        # machine.reset()
        
startLooping()
