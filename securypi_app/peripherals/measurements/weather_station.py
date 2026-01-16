import math

from flask import current_app
from securypi_app.models.measurement import Measurement
from securypi_app.peripherals.measurements.weather_station_interface import (
    WeatherStationInterface
)
from securypi_app.services.app_config import AppConfig

# sensors
from securypi_app.peripherals.measurements.sensors.sensor_dht22 import SensorDht22
from securypi_app.peripherals.measurements.sensors.sensor_sht30 import SensorSht30
from securypi_app.peripherals.measurements.sensors.sensor_qmp6988 import SensorQmp6988

# logger
from securypi_app.peripherals.measurements.measurement_logger import (
    MeasurementLogger
)


class WeatherStation(WeatherStationInterface):
    """
    Singleton wrapper for measuring and logging:
    - temperature
    - humidity
    - pressure
    From multiple different sensors which implement default interface.
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
        
        self.measurement_logger = MeasurementLogger(self)

        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def init_sensors(self):
        """ Set and initialize concrete sensors for measurement. """
        config = AppConfig.get()
        use_dht22 = config.measurements.sensors.use_dht22
        use_sht30 = config.measurements.sensors.use_sht30
        use_qmp6988 = config.measurements.sensors.use_qmp6988
        
        
        self._sensor_temperature = None
        self._sensor_humidity = None
        self._sensor_pressure = None
        
        if use_dht22:
            self._sensor_humidity = SensorDht22()
        elif use_sht30:
            self._sensor_humidity = SensorSht30()
        
        if use_qmp6988:
            self._sensor_pressure = SensorQmp6988()
        
        # Use the same sensor for temperature + humidity,
        # otherwise pressure + temperature
        if self._sensor_humidity is not None:
            self._sensor_temperature = self._sensor_humidity
        elif use_qmp6988:
            self._sensor_temperature = self._sensor_pressure
            

    def get_temperature(self, repeat=5) -> float | None:
        if self._sensor_temperature is not None:
            temp = self._sensor_temperature.sensor_read_temperature()
            if temp is not None:
                return temp
            elif repeat > 0:
                return self.get_temperature(repeat - 1)
        
        return None

    def get_humidity(self, repeat=5) -> float | None:
        if self._sensor_humidity is not None:
            hum = self._sensor_humidity.sensor_read_humidity()
            if hum is not None:
                return hum
            elif repeat > 0:
                return self.get_humidity(repeat - 1)
        
        return None
    
    def get_pressure(self, repeat=5) -> float | None:
        if self._sensor_pressure is not None:
            pres = self._sensor_pressure.sensor_read_pressure()
            if pres is not None:
                return pres
            elif repeat > 0:
                return self.get_humidity(repeat - 1)
        
        return None

    def measure(self, repeat=5) -> dict[str, float | None]:
        return {
            "temperature": self.get_temperature(),
            "humidity": self.get_humidity(),
            "pressure": self.get_pressure()
        }

    def present_measure_or_na(self,
                              round_digits=1,
                              temp_unit="C") -> dict[str, float | str]:
        measured = self.measure()
        temp = measured["temperature"]
        
        if temp is not None and temp_unit == "F":
            measured["temperature"] = self.c_to_fahrenheit(temp)
        
        values: dict[str, float | str] = {}
        for key, val in measured.items():
            if val is None:
                values[key] = "N/A"
            else:
                values[key] = round(val, round_digits)
        
        return values

    def measure_and_log(self) -> dict[str, float | None] | None:
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

    @staticmethod
    def c_to_fahrenheit(celsius: float) -> float:
        """ Convert Celsius to Fahrenheit. """
        return (celsius * 9/5) + 32

    @staticmethod
    def f_to_celsius(fahrenheit: float) -> float:
        """ Convert Fahrenheit to Celsius. """
        return (fahrenheit - 32) * 5/9

    @staticmethod
    def relative_pressure(pressure,
                          temperature,
                          elevation=None) -> float | str:
        """
        Converts absolute atmospheric pressure to relative pressure
        at sea level based on 'elevation' above sea level and 'temperature'.
        Returns "N/A" if inputs are not float.
        """
        if elevation is None:
            config = AppConfig.get()
            elevation = config.measurements.geolocation.elevation_meters
        try:
            pressure = float(pressure)
            temperature = float(temperature)
            elevation = float(elevation)
        except (TypeError, ValueError):
            return "N/A"
        
        gas_constant = 8.31432 # [N · m/(mol · K)] -> universal gas constant
        g = 9.81 # [m / s^2]
        air_molar_mass = 0.0289644 # [kg/mol]
        
        temperature_k = temperature + 273.15
        

        rel_pressure = pressure * math.exp(
            -g * air_molar_mass * (-elevation / (gas_constant * temperature_k))
        )
        return round(rel_pressure, 1)
