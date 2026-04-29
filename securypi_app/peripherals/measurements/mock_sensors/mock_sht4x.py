"""
Mock hardware sensor classes of WeatherStation
for platform independent development and testing.

- Sht40 connected to I2C
"""

from securypi_app.models.app_config import AppConfig


class MockSHT4x:
    """ Mock humidity and temperature sensor. """
    def __init__(self, i2c):
        self._i2c = i2c
        
        config = AppConfig.get()
        self._temperature = config.measurements.mock_sensors.mocked_temperature
        self._humidity = config.measurements.mock_sensors.mocked_humidity
    
    @property
    def temperature(self):
        return self._temperature

    @property
    def relative_humidity(self):
        return self._humidity
