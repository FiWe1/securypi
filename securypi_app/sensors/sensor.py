# conditional import for RPi DHT22 temp/humidity sensor
try:
    from adafruit_dht import DHT22  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]

except ImportError as e:
    print("Failed to import temperature sensor libraries, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    from .mock_temphum import MockDHT22, MockBoard

    DHT22 = MockDHT22
    board = MockBoard

"""
@TODO {
-CLASS
-singleton
-async thread, into @TODO ORM db!
"""


class Sensor(object):
    """
    My singleton wrapper class for Picamera2 with methods
    for streaming and taking pictures.
    """
    _instance = None
    _initialised = False

    def __new__(cls, *args, **kwargs):
        """ Guarantees only one instance - singleton. """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, pin=board.D4, temp_unit="C"):
        """ Initialise once. """
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.set_pin(pin).set_temp_unit(temp_unit)
        self.__sensor_device = DHT22(self.__pin)

        self._initialized = True

    @classmethod
    def get_instance(cls):
        """ Singleton access method. """
        return cls()


    def set_pin(self, pin):
        """ Set GPIO pin=board.D{number} for sensor data. """
        self.__pin = pin
        return self

    def get_temp_unit(self):
        return self.__temp_unit

    def set_temp_unit(self, unit):
        """ Set temperature unit = 'C' | 'F'. """
        if unit in ["C", "F"]:
            self.__temp_unit = unit
        return self

    def get_temperature(self):
        """ Get temperature in desired unit. (DHT22 device reading C)"""
        temperature = self.__sensor_device.temperature
        if self.__temp_unit == "C":
            return temperature
        elif self.__temp_unit == "F":
            return temperature * (9 / 5) + 32
        else:
            raise ValueError("Invalid unit. Use 'C' for Celsius "
                             "or 'F' for Fahrenheit.")

    def get_humidity(self):
        """ Get humidity. (DHT22 device). """
        return self.__sensor_device.humidity

    def measure(self) -> dict[float | str, float | str]:
        """ Measure temperature and humidity using sensor device."""
        try:
            measurements = {
                "temperature": self.get_temperature(),
                "humidity": self.get_humidity()
            }
        except Exception as err:
            print(f"Failed to read from temperature sensor: {err}")
            measurements = {
                "temperature": "N/A",
                "humidity": "N/A"
            }

        return measurements
