from threading import Thread, Event
from time import sleep
from abc import ABC, abstractmethod

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
LOGGING_INTERVAL_SEC = 30
LOG_WEATHER_IN_BACKGROUND = True


class WeatherStationInterface(ABC):
    """
    Interface for WeatherSensor's public methods.
    Must Not be instanciated.
    """
    @classmethod
    @abstractmethod
    def get_instance(cls):
        """ Singleton access method. """
        pass

    @abstractmethod
    def set_pin(self, pin: board):  # type: ignore
        """ Set GPIO pin=board.D{number} for sensor data. """
        pass

    @abstractmethod
    def get_temperature(self) -> float | None:
        """ Get temperature in Celsius. (DHT22 sensor). """
        pass

    @abstractmethod
    def get_humidity(self) -> float | None:
        """ Get humidity in %. (DHT22 sensor). """
        pass

    @abstractmethod
    def measure(self, repeat) -> dict[str, float] | None:
        """ 
        Measure temperature and humidity using sensor device.
        On failure, retry 'repeat' times before returning None.
        """
        pass

    @abstractmethod
    def measure_or_na(self, temp_unit="C") -> dict[float | str, float | str]:
        """ 
        Measure temperature and humidity, on failure format the results:
        return dict{x: "N/A", ..., z: "N/A"}.
        Convert temerature to specified unit:
        "C" (Celsius) or "F" (Fahrenheit)
        """
        pass

    @abstractmethod
    def measure_and_log(self) -> dict[str, float] | None:
        """
        Measure temperature and humidity and store in db.
        On success return dictionary of measured values, None othervise.
        """
        pass

    # Background measurement logging into database.
    @abstractmethod
    def is_logging(self) -> bool:
        """ Is background logger running? """
        pass

    @abstractmethod
    def set_log_in_background(self, set: bool):
        """ Set and start/stop background logging. """
        pass

    @abstractmethod
    def get_logging_interval(self) -> int:
        pass

    @abstractmethod
    def set_logging_interval(self, seconds: int):
        """
        Update logging interval.
        If logging is running, restart and log in this interval.
        """
        pass


class WeatherStation(WeatherStationInterface):
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
        self._app = current_app._get_current_object() # pyright: ignore[reportAttributeAccessIssue]

        # sensor
        self.set_pin(pin)
        self._sensor = DHT22(self._pin)

        # background logging
        self._logging_thread = None
        self._logging_stop_event = Event()
        self.apply_logging_config()

        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    def set_pin(self, pin):
        self._pin = pin
        return self

    def get_temperature(self) -> float | None:
        try:
            readout = self._sensor.temperature
        except Exception as err:
            readout = None
            print(f"Failed to read from temperature sensor: {err}")
        return readout

    def get_humidity(self) -> float | None:
        try:
            readout = self._sensor.humidity
        except Exception as err:
            readout = None
            print(f"Failed to read from temperature sensor: {err}")
        return readout

    def measure(self, repeat=5) -> dict[str, float] | None:
        temperature = self.get_temperature()
        humidity = self.get_humidity()

        if temperature is not None and humidity is not None:
            return {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1)
            }

        if repeat > 0:
            return self.measure(repeat=(repeat - 1))

        return None

    def measure_or_na(self, temp_unit="C") -> dict[str, float] | dict[str, str]:
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

    def measure_and_log(self) -> dict[str, float] | None:
        values = self.measure()

        if values is not None:
            new_measurement = Measurement(
                temperature=values["temperature"],
                humidity=values["humidity"]
            )
            if not new_measurement.log():
                return None

        return values

    def logger(self):
        """
        Countinuously log sensor measurements to the database
        in configured interval.
        """
        sleep(2)  # avoid sensor colisions on start # @TODO remove with sht30
        # The new thread needs app context in order to have access
        # to app variables, access to database
        with self._app.app_context():
            while True:
                self.measure_and_log()
                interval = self._logging_interval
                if self._logging_stop_event.wait(timeout=interval):
                    print("Background WeatherSensor logger exited cleanly.")
                    break

    def is_logging(self) -> bool:
        return self._logging_thread is not None

    def apply_logging_config(self):
        """ Load and apply background logging configuration. """
        # @TODO: from json
        self._log_in_background = LOG_WEATHER_IN_BACKGROUND
        self._logging_interval = LOGGING_INTERVAL_SEC
        if self._log_in_background:
            self.start_logging()

    def set_log_in_background(self, set: bool):
        self._log_in_background = set
        # @TODO: update json
        if set:
            self.start_logging()
        else:
            self.stop_logging()

    def get_logging_interval(self) -> int:
        return self._logging_interval

    def set_logging_interval(self, seconds: int):
        self._logging_interval = seconds
        # @TODO: update json
        if self.is_logging():
            self.start_logging()  # restarts the running logging

    def start_logging(self):
        """
        Start background measurement logging.
        If logging was running, restart it.
        """
        if self.is_logging():
            print("Background WeatherSensor logger was not stopped, "
                  "stopping now...")
            self.stop_logging()

        self._logging_thread = (
            Thread(target=self.logger)
        )
        self._logging_stop_event.clear()  # clear stop signal
        self._logging_thread.start()
        print("Background WeatherSensor logging has started")

    def stop_logging(self):
        if self.is_logging():
            self._logging_stop_event.set()  # signal stop
            if self._logging_thread:
                self._logging_thread.join()

            self._logging_thread = None
        else:
            print("Can't stop background WeatherSensor logger, "
                  "it is not running.")

    @staticmethod
    def c_to_fahrenheit(celsius: float) -> float:
        """ Convert Celsius to Fahrenheit. """
        return (celsius * 9/5) + 32

    @staticmethod
    def f_to_celsius(fahrenheit: float) -> float:
        """ Convert Fahrenheit to Celsius. """
        return (fahrenheit - 32) * 5/9
