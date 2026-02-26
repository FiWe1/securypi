"""
Interfaces for standardized measurement access methods
accross all different sensors.

To add a new sensor, you only need to implement the sensor interface
and assign your sensor class in peripherals/measurements/weather_station.py's
"init_sensors" method.
"""
from abc import ABC, abstractmethod


class TemperatureSensorInterface(ABC):
    
    @abstractmethod
    def sensor_read_temperature(self) -> float:
        """
        Return float temperature sensor value in Celsius
        (without handling errors)
        """
        pass

    @abstractmethod
    def sensor_close(self):
        pass


class HumiditySensorInterface(ABC):
    
    @abstractmethod
    def sensor_read_humidity(self) -> float:
        """
        Return float relative humidity sensor value in %
        (without handling errors)
        """
        pass
    
    @abstractmethod
    def sensor_close(self):
        pass


class PressureSensorInterface(ABC):
    
    @abstractmethod
    def sensor_read_pressure(self) -> float:
        """
        Return float absolute pressure sensor value in hPa
        (without handling errors)
        """
        pass
    
    @abstractmethod
    def sensor_close(self):
        pass