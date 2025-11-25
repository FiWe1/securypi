import pytest
from time import sleep

from securypi_app import create_app
from securypi_app.models.measurement import Measurement
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
        sensor._logging_stop_event.set()
        if sensor.is_logging():
            sensor._logging_thread.join()
            sensor._logging_thread = None
        sensor._logging_stop_event.clear()

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

    def test_logging_running(self, sensor):
        sensor.stop_logging()
        sensor.stop_logging()
        assert not sensor.is_logging()

        sensor.start_logging()
        sensor.start_logging()
        assert sensor.is_logging()

        sensor.stop_logging()
        assert not sensor.is_logging()

    def test_logging(self, sensor):
        old_mes = Measurement.fetch_latest()
        old_time = old_mes.time

        sensor.start_logging()
        sleep(3)

        new_mes = Measurement.fetch_latest()
        new_time = new_mes.time

        assert old_time < new_time
    
    def test_set_logging_interval(self, sensor):
        """
        Setting a new background measurement interval should result
        in an immediate change (don't want to be stuck)
        """
        old_interval = sensor.get_logging_interval()
        try:
            sensor.set_logging_interval(60)
            sleep(3)
            first_mes = Measurement.fetch_latest()
            
            sensor.set_logging_interval(5)
            sleep(3)
            second_mes = Measurement.fetch_latest()
            
            sleep(5)
            third_mes = Measurement.fetch_latest()
            assert first_mes.time < second_mes.time < third_mes.time
            
        finally:
            # reapply the previous value
            sensor.set_logging_interval(old_interval)
        


    C_TO_F_DATA = [
        (0, 32.0),
        (100, 212.0),
        (-40, -40.0),
        (20, 68.0),
        (37, 98.6)
    ]
    # static methods
    @pytest.mark.parametrize("celsius,fahrenheit", C_TO_F_DATA)
    def test_conversions(self, sensor, celsius, fahrenheit):
        c_result = sensor.f_to_celsius(fahrenheit)
        assert celsius == c_result

        f_result = sensor.c_to_fahrenheit(celsius)
        assert fahrenheit == f_result
