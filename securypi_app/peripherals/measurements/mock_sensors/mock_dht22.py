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
        
        config = AppConfig.get()
        self._temperature = config.measurements.mock_sensors.mocked_temperature
        self._humidity = config.measurements.mock_sensors.mocked_humidity
    
    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity

    def exit(self):
        pass
