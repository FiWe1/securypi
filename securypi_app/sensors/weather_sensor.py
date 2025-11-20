from securypi_app import db
from securypi_app.models.measurement import Measurement

# conditional import for RPi DHT22 temp/humidity sensor
try:
    from adafruit_dht import DHT22  # pyright: ignore[reportMissingImports]
    import board                    # pyright: ignore[reportMissingImports]

except ImportError as e:
    print("Failed to import temperature sensor libraries, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    from .mock_weather_sensor import MockDHT22, MockBoard

    DHT22 = MockDHT22
    board = MockBoard


# @TODO async thread, into ORM db!
class WeatherSensor(object):
    """
    Singleton class for reading temperature and humidity.
    Uses DHT22 sensor connected to specified GPIO pin.
    """
    _instance = None
    _initialised = False

    def __new__(cls, *args, **kwargs):
        """ Guarantees only one instance - singleton. """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, pin=board.D4):
        """ Initialise once. """
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.set_pin(pin)
        self._sensor = DHT22(self.__pin)

        self._initialized = True

    @classmethod
    def get_instance(cls):
        """ Singleton access method. """
        return cls()

    def set_pin(self, pin):
        """ Set GPIO pin=board.D{number} for sensor data. """
        self.__pin = pin
        return self

    def get_temperature(self):
        """ Get temperature in Celsius. (DHT22 sensor). """
        return self._sensor.temperature

    def get_humidity(self):
        """ Get humidity. (DHT22 sensor). """
        return self._sensor.humidity

    def measure(self, repeat=5) -> dict[float] | None:
        """ 
        Measure temperature and humidity using sensor device.
        On failure, retry 'repeat' times before returning None.
        """
        try:    
            measurements = {
                "temperature": self.get_temperature(),
                "humidity": self.get_humidity()
            }
        except Exception as err:
            if repeat > 0:
                return self.measure(repeat=(repeat - 1))
            
            print(f"Failed to read from temperature sensor: {err}")
            measurements = None
        
        return measurements
    
    def measure_or_na(self, temp_unit="C") -> dict[float | str, float | str]:
        """ 
        Measure temperature and humidity, return dict["N/A", ...] on failure.
        Convert temerature to specified
        unit: "C" (Celsius) or "F" (Fahrenheit).
        """
        values = self.measure()
        
        if values is None:
            values = {
                "temperature": "N/A",
                "humidity": "N/A"
            }
        elif temp_unit == "F":
            values["temperature"] = self.c_to_fahrenheit(
                values["temperature"]
            )
        return values
    
    def measure_and_log(self) -> dict[float] | None:
        """ Measure temperature and humidity and store in db. """
        values = self.measure()
        
        if values is not None:
            new_measurement = Measurement(
                temperature=values["temperature"],
                humidity=values["humidity"]
            )
            db.session.add(new_measurement)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
                return None
        
        return values

    @staticmethod
    def c_to_fahrenheit(celsius: float) -> float:
        """ Convert Celsius to Fahrenheit. """
        return (celsius * 9/5) + 32
    
    @staticmethod
    def f_to_celsius(self, fahrenheit: float) -> float:
        """ Convert Fahrenheit to Celsius. """
        return (fahrenheit - 32) * 5/9