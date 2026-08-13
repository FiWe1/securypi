"""
Mock hardware sensor classes of WeatherStation
for platform independent development and testing.

- Sht30 connected to I2C
"""

from securypi_app.models.app_config import AppConfig


class MockSHT31D:
    """ Mock humidity and temperature sensor. """
    def __init__(self, i2c):
        self._i2c = i2c

    @property
    def temperature(self):
        return AppConfig.get().measurements.mock_sensors.mocked_temperature

    @property
    def relative_humidity(self):
        return AppConfig.get().measurements.mock_sensors.mocked_humidity
