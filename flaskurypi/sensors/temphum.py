import time
import adafruit_dht
import board


def measure_temp_hum(pin = board.D4, temperature_unit = 'C'):
    try:
        dht_device = adafruit_dht.DHT22(pin)
        
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        
        if temperature_unit == 'C':
            temperature = temperature_c
        elif temperature_unit == 'F':
            temperature = temperature_c * (9 / 5) + 32
        else:
            raise ValueError("Invalid unit. Use 'C' for Celsius or 'F' for Fahrenheit.")
        
        dht_device.exit()
        return temperature, humidity
    except RuntimeError as err:
        print(err.args[0])
        return None, None
