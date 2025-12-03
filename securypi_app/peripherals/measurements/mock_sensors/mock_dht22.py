"""
Mock hardware sensor classes of WeatherSensor
for platform independent development and testing.

- DHT22 connected to gpio4
"""

MOCKED_TEMPERATURE = -273.15
MOCKED_HUMIDITY = 0.0


class MockDHT22:
    """ Mock humidity and temperature sensor. """
    def __init__(self, pin=None):
        self._pin = pin
    
    @property
    def temperature(self):
        return MOCKED_TEMPERATURE

    @property
    def humidity(self):
        return MOCKED_HUMIDITY

    def exit(self):
        pass
