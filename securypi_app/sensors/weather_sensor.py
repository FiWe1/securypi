from threading import Thread, Event
from time import sleep

from flask import current_app
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


# @TODO move to centralised serialised json config
MEASUREMENT_LOGGING_INTERVAL_SEC = 30


class WeatherSensor(object):
    """
    Singleton class for reading temperature and humidity.
    Uses DHT22 sensor connected to specified GPIO pin.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """ Guarantees only one instance - singleton. """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, pin=board.D4):
        """ Initialise once. """
        if self._initialized:
            return
        super().__init__()
        self._app = current_app._get_current_object()
        self.set_pin(pin)
        self._sensor = DHT22(self.__pin)
        self._background_logger_thread = None
        self._background_logger_stop_event = Event()

        # implicitly log in background
        self.start_background_logger()

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
            temperature = self.get_temperature()
            humidity = self.get_humidity()
            if temperature is None or humidity is None:
                measurements = None
            else:
                measurements = {
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1)
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
            if not new_measurement.log():
                return None

        return values

    def background_loger(self):
        """
        Countinuously log sensor measurements to the database
        in configured interval, until signalized on:
        self._background_logger_stop_event.set()
        """
        sleep(2)  # avoid sensor colisions on start # @TODO remove with sht30
        # The new thread needs app context in order to have access
        # to app variables, access to database
        with self._app.app_context():
            while True:
                self.measure_and_log()
                interval = MEASUREMENT_LOGGING_INTERVAL_SEC
                if self._background_logger_stop_event.wait(timeout=interval):
                    print("Background WeatherSensor logger exited cleanly.")
                    break

    def is_background_logging(self) -> bool:
        return self._background_logger_thread is not None

    def start_background_logger(self):
        if self.is_background_logging():
            print("Background WeatherSensor logger was not stopped, "
                  "stopping now...")
            self.stop_background_logger()

        self._background_logger_thread = (
            Thread(target=self.background_loger)
        )
        self._background_logger_stop_event.clear()  # clear stop signal
        self._background_logger_thread.start()
        print("Background WeatherSensor logging has started")

    def stop_background_logger(self):
        if self.is_background_logging():
            self._background_logger_stop_event.set()  # signal stop
            self._background_logger_thread.join()

            self._background_logger_thread = None
        else:
            print("Can't stop background WeatherSensor logger, "
                  "it is not running.")

    @staticmethod
    def c_to_fahrenheit(celsius: float) -> float:
        """ Convert Celsius to Fahrenheit. """
        return (celsius * 9/5) + 32

    @staticmethod
    def f_to_celsius(self, fahrenheit: float) -> float:
        """ Convert Fahrenheit to Celsius. """
        return (fahrenheit - 32) * 5/9
