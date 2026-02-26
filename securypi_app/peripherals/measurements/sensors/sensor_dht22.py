from securypi_app.peripherals.measurements.sensors.sensor_interface import (
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
    from securypi_app.peripherals.measurements.mock_sensors.mock_dht22 import (
        MockDHT22
    )
    from securypi_app.peripherals.measurements.mock_sensors.mock_board import (
        MockBoard
    )

    DHT22 = MockDHT22
    board = MockBoard


class SensorDht22(TemperatureSensorInterface,
                  HumiditySensorInterface):
    
    def __init__(self):
        super().__init__()
        
        # gpio pin
        self._pin = board.D4
        self._sensor = DHT22(self._pin)
    
    def sensor_read_temperature(self, repeat=5) -> float:
        return float(self._sensor.temperature)
    
    def sensor_read_humidity(self, repeat=5) -> float:
        return float(self._sensor.humidity)

    def sensor_close(self):
        self._sensor.exit()
