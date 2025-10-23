
try:
    from adafruit_dht import DHT22  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]
    
except ImportError:
    # Mock sensor classes for development outside RPi
    from sensors.temphum_mock import MockDHT22, MockBoard
        
    DHT22 = MockDHT22
    board = MockBoard


def measure_temp_hum(pin = board.D4, temperature_unit = 'C'):
    """ Measure temperature and humidity using DHT22 sensor."""
    try:
        dht_device = DHT22(pin)
        
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        
        if temperature_unit == 'C':
            temperature = temperature_c
        elif temperature_unit == 'F':
            temperature = temperature_c * (9 / 5) + 32
        else:
            raise ValueError("Invalid unit. Use 'C' for Celsius or 'F' for Fahrenheit.")
        
        return temperature, humidity
    except RuntimeError as err:
        print(err.args[0])
        return None, None
    finally:
        dht_device.exit()