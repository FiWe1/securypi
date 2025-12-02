"""
Mock hardware sensor classes of WeatherStation
for platform independent development and testing.

- Sht30 connected to I2C
"""

MOCKED_TEMPERATURE = -273.15
MOCKED_HUMIDITY = 0.0


class MockSHT31D:
    """ Mock humidity and temperature sensor. """
    def __init__(self, i2c):
        self._i2c = i2c
    
    @property
    def temperature(self):
        return MOCKED_TEMPERATURE

    @property
    def relative_humidity(self):
        return MOCKED_HUMIDITY
