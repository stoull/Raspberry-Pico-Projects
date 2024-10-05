from machine import Pin
import dht


led_pin = Pin("LED", Pin.OUT)  # GPIO pin 25 controls the onboard LED
dSensor = dht.DHT22(Pin(2))
def readDHT():
    led_pin.on()  # Toggle the LED state
    try:
        dSensor.measure()
        temp = dSensor.temperature()
        temp_f = (temp * (9 / 5)) + 32.0
        hum = dSensor.humidity()
        # print('Temperature= {} C, {} F'.format(temp, temp_f))
        # print('Humidity= {} '.format(hum))
        led_pin.off()
        return (temp, hum)
    except OSError as e:
        print(f'the error is : {e}')
        led_pin.off()
        return None
