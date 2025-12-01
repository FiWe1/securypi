from threading import Thread, Event
from time import sleep
from abc import ABC, abstractmethod

from flask import current_app
from securypi_app.models.measurement import Measurement

# sensors
from securypi_app.sensors.sensor_dht22 import SensorDht22
from securypi_app.sensors.sensor_sht30 import SensorSht30
from securypi_app.sensors.sensor_qmp6988 import SensorQmp6988



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
    def present_measure_or_na(self,
                              round_digits=1,
                              temp_unit="C") -> dict[float | str, float | str]:
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

    def __init__(self):
        """ Initialise once. """
        if self._initialized:
            return
        super().__init__()
        self._app = current_app._get_current_object() # pyright: ignore[reportAttributeAccessIssue]
        self.init_sensors()

        # background logging
        self._logging_thread = None
        self._logging_stop_event = Event()
        self.apply_logging_config()

        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def init_sensors(self):
        """ Set and initialize concrete sensors for measurement. """
        self._sensor_humidity = SensorSht30()
        self._sensor_pressure = SensorQmp6988()
        
        self._sensor_temperature = self._sensor_humidity

    def get_temperature(self) -> float | None:
        if self._sensor_temperature is not None:
            return self._sensor_temperature.sensor_read_temperature()

    def get_humidity(self) -> float | None:
        if self._sensor_humidity is not None:
            return self._sensor_humidity.sensor_read_humidity()
    
    def get_pressure(self) -> float | None:
        if self._sensor_pressure is not None:
            return self._sensor_pressure.sensor_read_pressure()

    def measure(self, repeat=5) -> dict[str, float | None]:
        return {
            "temperature": self.get_temperature(),
            "humidity": self.get_humidity(),
            "pressure": self.get_pressure()
        }

    def present_measure_or_na(self,
                              round_digits=1,
                              temp_unit="C") -> dict[str, float] | dict[str, str]:
        values = self.measure()
        temp = values["temperature"]
        
        if temp is not None and temp_unit == "F":
            values["temperature"] = self.c_to_fahrenheit(temp)
            
        for key, val in values.items():
            if val == None:
                values[key] = "N/A"
            else:
                values[key] = round(val, round_digits)
        
        return values

    def measure_and_log(self) -> dict[str, float] | None:
        measurements = self.measure()

        if any(value is not None for value in measurements.values()):
            new_measurement = Measurement(
                temperature=measurements["temperature"],
                humidity=measurements["humidity"],
                pressure=measurements["pressure"]
            )
            if not new_measurement.log():
                return None

        return measurements

    def logger(self):
        """
        Countinuously log sensor measurements to the database
        in configured interval.
        """
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
