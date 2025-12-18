from abc import ABC, abstractmethod


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
    def get_temperature(self, repeat=5) -> float | None:
        """
        Get temperature in Celsius from initialized temperature sensor.
        On fail, retry 'repeat' times.
        """
        pass

    @abstractmethod
    def get_humidity(self, repeat=5) -> float | None:
        """
        Get relative humidity in % from initialized humidity sensor.
        On fail, retry 'repeat' times.
        """
        pass
    
    @abstractmethod
    def get_pressure(self, repeat=5) -> float | None:
        """
        Get absolute pressure in hPa from initialized pressure sensor.
        On fail, retry 'repeat' times.
        """
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
