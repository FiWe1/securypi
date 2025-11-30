from securypi_app.sensors.sensor_interface import (
    TemperatureSensorInterface, HumiditySensorInterface
)

# conditional import for RPi DHT22 temp/humidity sensor
try:
    from adafruit_sht31d import SHT31D  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]

except ImportError as e:
    print("Failed to import temperature sensor libraries, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    # from .mock_weather_sensor import MockDHT22, MockBoard

    # DHT22 = MockDHT22
    # board = MockBoard
    # TODO MoCK


class SensorSht30(TemperatureSensorInterface,
                   HumiditySensorInterface):
    
    def __init__(self):
        super().__init__()
        
        self._sensor = SHT31D(board.I2C())
    
    def sensor_read_temperature(self) -> float | None:
        try:
            temp = self._sensor.temperature
        except Exception as err:
            print(f"Failed to read from SHT30 temperature sensor: {err}")
            return None
        
        return round(float(temp), 2)
    
    def sensor_read_humidity(self) -> float | None:
        try:
            hum = self._sensor.relative_humidity
        except Exception as err:
            print(f"Failed to read from SHT30 humidity sensor: {err}")
            return None
        
        return round(float(hum), 2)

    def sensor_close(self):
        pass
