"""
Mock hardware sensor classes of WeatherSensor
for platform independent development and testing.

- DHT22 connected to gpio4
"""

from securypi_app.models.app_config import AppConfig


class MockDHT22:
    """ Mock humidity and temperature sensor. """
    def __init__(self, pin=None):
        self._pin = pin

    @property
    def temperature(self):
        return AppConfig.get().measurements.mock_sensors.mocked_temperature

    @property
    def humidity(self):
        return AppConfig.get().measurements.mock_sensors.mocked_humidity

    def exit(self):
        pass
