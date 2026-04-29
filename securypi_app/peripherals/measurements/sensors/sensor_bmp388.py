import logging
import time

from securypi_app.peripherals.measurements.sensors.sensor_interface import (
    PressureSensorInterface, TemperatureSensorInterface
)

# conditional import for RPi BMP388 pressure/temperature sensor
try:
    from adafruit_bmp3xx import BMP3XX_I2C  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]

except ImportError as e:
    logging.warning("Failed to import BMP388 sensor libraries, reverting to mock class: %s", e)
    # Mock sensor classes for platform independent development
    from securypi_app.peripherals.measurements.mock_sensors.mock_bmp3xx_i2c import (
        MockBMP3XX_I2C
    )
    import securypi_app.peripherals.measurements.mock_sensors.mock_board as board

    BMP3XX_I2C = MockBMP3XX_I2C


class SensorBmp388(PressureSensorInterface, TemperatureSensorInterface):
    
    def __init__(self):
        super().__init__()
        
        i2c = board.I2C()
        self._sensor = BMP3XX_I2C(i2c)
        
        # solves hang on init:
        self._sensor.pressure_oversampling = 2
        self._sensor.temperature_oversampling = 2
        
        self._initialized = True
        
    def sensor_read_pressure(self) -> float:
        return float(self._sensor.pressure)
            
    def sensor_read_temperature(self) -> float:
        return float(self._sensor.temperature)

    def sensor_close(self):
        pass
