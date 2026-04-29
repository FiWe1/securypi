import logging

from securypi_app.peripherals.measurements.sensors.sensor_interface import (
    TemperatureSensorInterface, HumiditySensorInterface
)

# conditional import for RPi SHT40 temp/humidity sensor
try:
    from adafruit_sht4x import SHT4x  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]

except ImportError as e:
    logging.warning("Failed to import SHT30 sensor libraries, reverting to mock class: %s", e)
    # Mock sensor classes for platform independent development
    from securypi_app.peripherals.measurements.mock_sensors.mock_sht4x import (
        MockSHT4x
    )
    import securypi_app.peripherals.measurements.mock_sensors.mock_board as board

    SHT4x = MockSHT4x


class SensorSht40(TemperatureSensorInterface,
                   HumiditySensorInterface):
    
    def __init__(self):
        super().__init__()
        
        self._sensor = SHT4x(board.I2C())
    
    def sensor_read_temperature(self) -> float:
        return float(self._sensor.temperature)
    
    def sensor_read_humidity(self) -> float:
        return float(self._sensor.relative_humidity)

    def sensor_close(self):
        pass
