# needs executed:
# sudo pigpiod

from securypi_app.peripherals.measurements.sensors.sensor_interface import (
    TemperatureSensorInterface, PressureSensorInterface
)

# conditional import for RPi DHT22 temp/humidity sensor
try:
    import piqmp6988 as QMP  # pyright: ignore[reportMissingImports]

except ImportError as e:
    print("Failed to import temperature sensor libraries, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    from securypi_app.peripherals.measurements.mock_sensors.mock_qmp6988 import (
        MockQMP as QMP
    )
    

# configuration: adjust if needed
config = {
    'temperature': QMP.Oversampling.X4.value,
    'pressure':    QMP.Oversampling.X32.value,
    'filter':      QMP.Filter.COEFFECT_32.value,
    'mode':        QMP.Powermode.NORMAL.value
}


class SensorQmp6988(PressureSensorInterface, TemperatureSensorInterface):
    
    def __init__(self):
        super().__init__()
        
        self._sensor = QMP.PiQmp6988(config)
    
    def sensor_read_pressure(self) -> float | None:
        readout = self._sensor.read()
        pres = readout.get('pressure')
        
        if isinstance(pres, float):
            return round(pres, 2)
        
        return None
    
    def sensor_read_temperature(self) -> float | None:
        readout = self._sensor.read()
        temp = readout.get('temperature')
        
        if isinstance(temp, float):
            return round(temp, 2)

        return None

    def sensor_close(self):
        pass
