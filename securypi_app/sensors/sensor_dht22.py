from securypi_app.sensors.sensor_interface import (
    TemperatureSensorInterface, HumiditySensorInterface
)

# conditional import for RPi DHT22 temp/humidity sensor
try:
    from adafruit_dht import DHT22  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]

except ImportError as e:
    print("Failed to import temperature sensor libraries, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    from securypi_app.sensors.mock_sensors.mock_dht22 import MockDHT22
    from securypi_app.sensors.mock_sensors.mock_board import MockBoard

    DHT22 = MockDHT22
    board = MockBoard


class SensorDht22(TemperatureSensorInterface,
                  HumiditySensorInterface):
    
    def __init__(self):
        super().__init__()
        
        # gpio pin
        self._pin = board.D4
        self._sensor = DHT22(self._pin)
    
    def sensor_read_temperature(self, repeat=5) -> float | None:
        try:
            temp = self._sensor.temperature
        except Exception as err:
            print(f"Failed to read from DHT22 temperature sensor: {err}")
            if repeat > 0:
                return self.sensor_read_temperature(repeat=(repeat - 1))
            
            return None
        
        return round(float(temp), 2)
    
    def sensor_read_humidity(self, repeat=5) -> float | None:
        try:
            hum = self._sensor.humidity
        except Exception as err:
            print(f"Failed to read from DHT22 humidity sensor: {err}")
            if repeat > 0:
                return self.sensor_read_humidity(repeat=(repeat - 1))
        
        return round(float(hum), 2)

    def sensor_close(self):
        self._sensor.exit()
