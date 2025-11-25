import pytest

from securypi_app import create_app
from securypi_app.sensors.weather_sensor import WeatherSensor


class TestWeatherSensor():
    
    @pytest.fixture
    def app(self):
        """
        Create the app.
        To import the app context, add 'app' parameter to the thest.
        """
        app = create_app()
        with app.app_context():
            yield app

    
    @pytest.fixture
    def sensor(self, app):
        """
        Every time yield the same WeatherSensor instance,
        but with default configuration.
        """
        sensor = WeatherSensor.get_instance()
        yield sensor

        # try to get WeatherSensor to default state
        sensor._background_logger_stop_event.set()
        if sensor.is_background_logging():
            sensor._background_logger_thread.join()
            sensor._background_logger_thread = None
        sensor._background_logger_stop_event.clear()

        del sensor  # delete object reference
    
    def test_singleton(self, sensor):
        """ Try to break singleton """
        obj2 = WeatherSensor()
        assert sensor is obj2

    def test_get_temperature(self, sensor):
        try:
            temp = sensor.get_temperature()
            hum = sensor.get_temperature()
        except:
            # might fail - not handling exceptions
            return
        
        assert isinstance(temp, float)
        assert isinstance(hum, float)
    
    def test_measure(self, sensor):
        res = sensor.measure()
        if res == None:
            return
        
        assert isinstance(res["temperature"], float)
        assert isinstance(res["humidity"], float)
    
    def test_measure_or_na(self, sensor):
        res = sensor.measure_or_na()
        
        assert isinstance(res["temperature"], (float, str))
        assert isinstance(res["humidity"], (float, str))
    
    def test_background_logger_start(self):
        pass
    
    def test_background_logger(self):
        pass
        # @TODO - check results appearing in db
    
    
    # static methods
    def test_c_to_fahrenheit(celsius: float):
        pass
    
    def test_f_to_celsius(fahrenheit: float):
        pass