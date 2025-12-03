from abc import ABC, abstractmethod


class MeasurementLoggerInterface(ABC):
    """
    Public interface for MeasurementLogger methods.
    Must Not be instanciated.
    """
    
    @abstractmethod
    def __init__(self, weather_station):
        """ Must be initialized with WeatherStation instance. """
        pass
    
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
