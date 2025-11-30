"""
Interfaces for standardized measurement access methods
accross all different sensors.
"""
from abc import ABC, abstractmethod


class TemperatureSensorInterface(ABC):
    
    @abstractmethod
    def sensor_read_temperature(self) -> float | None:
        pass

    @abstractmethod
    def sensor_close(self):
        pass


class HumiditySensorInterface(ABC):
    
    @abstractmethod
    def sensor_read_humidity(self) -> float | None:
        pass
    
    @abstractmethod
    def sensor_close(self):
        pass


class PressureSensorInterface(ABC):
    
    @abstractmethod
    def sensor_read_pressure(self) -> float | None:
        pass
    
    @abstractmethod
    def sensor_close(self):
        pass