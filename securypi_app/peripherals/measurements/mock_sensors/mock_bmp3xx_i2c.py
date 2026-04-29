"""
Mock hardware sensor classes of WeatherStation
for platform independent development and testing.

- bmp388 connected to I2C
"""

from securypi_app.models.app_config import AppConfig


class MockBMP3XX_I2C:
    """ Mock humidity and temperature sensor. """
    def __init__(self, i2c):
        self._i2c = i2c
        
        config = AppConfig.get()
        self._temperature = config.measurements.mock_sensors.mocked_temperature
        self._pressure = config.measurements.mock_sensors.mocked_pressure
    
    @property
    def temperature(self):
        return self._temperature

    @property
    def pressure(self):
        return self._pressure
