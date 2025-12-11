from machine import Pin
import dht
import time

led_pin = Pin("LED", Pin.OUT)  # GPIO pin 25 controls the onboard LED
dSensor = dht.DHT22(Pin(2))
log_file = open("_log_sensor.txt", "w")
log_file.flush()
def readDHT():
    led_pin.off()  # Toggle the LED state
    try:
        dSensor.measure()
        temp = dSensor.temperature()
        temp_f = (temp * (9 / 5)) + 32.0
        hum = dSensor.humidity()
        # print('Temperature= {} C, {} F'.format(temp, temp_f))
        # print('Humidity= {} '.format(hum))
        led_pin.on()
        startTime_str = "dht22 get：%s" %str(time.localtime()) + 'temp= {} C'.format(temp)
        log_file.write(startTime_str + "\n")
        return (temp, hum)
    except Exception as e:
        # print(f'the error is : {e}')
        led_pin.off()
        log_file.write(startTime_str + "\n")
        log_file.write("dht22 error: %s" %str(e))
        return e