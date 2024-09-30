import machine
import time
from machine import Pin
import dht

import time

led_pin = machine.Pin("LED", machine.Pin.OUT)  # GPIO pin 25 controls the onboard LED
dSensor = dht.DHT22(Pin(2))
def readDHT():
    led_pin.on()  # Toggle the LED state
    try:
        dSensor.measure()
        temp = dSensor.temperature()
        temp_f = (temp * (9 / 5)) + 32.0
        hum = dSensor.humidity()
        print('Temperature= {} C, {} F'.format(temp, temp_f))
        print('Humidity= {} '.format(hum))
    except OSError as e:
        print('Failed to read data from DHT sensor')
    led_pin.off()


while True:
    print("Running...")
    readDHT()
    time.sleep(10)