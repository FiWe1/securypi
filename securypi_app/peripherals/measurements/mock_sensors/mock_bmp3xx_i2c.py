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

    @property
    def temperature(self):
        return AppConfig.get().measurements.mock_sensors.mocked_temperature

    @property
    def pressure(self):
        return AppConfig.get().measurements.mock_sensors.mocked_pressure
