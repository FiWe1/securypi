import pytest
from time import sleep

from securypi_app import create_app
from securypi_app.models.measurement import Measurement
from securypi_app.peripherals.measurements.weather_station import WeatherStation


class TestWeatherStation():

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
    def station(self, app):
        """
        Every time yield the same Weatherstation instance,
        but with default configuration.
        """
        station = WeatherStation.get_instance()
        yield station

        # try to get Weatherstation to default state
        station.measurement_logger._logging_stop_event.set()
        if station.measurement_logger.is_logging():
            if station.measurement_logger._logging_thread is not None:
                station.measurement_logger._logging_thread.join()
                station.measurement_logger._logging_thread = None
        station.measurement_logger._logging_stop_event.clear()

        del station  # delete object reference

    def test_singleton(self, station):
        """ Try to break singleton """
        obj2 = WeatherStation()
        assert station is obj2

    def test_get_temperature(self, station):
        try:
            temp = station.get_temperature()
            hum = station.get_temperature()
        except:
            # might fail - not handling exceptions
            return

        assert isinstance(temp, float)
        assert isinstance(hum, float)

    def test_measure(self, station):
        res = station.measure()
        if res == None:
            return

        assert isinstance(res["temperature"], float)
        assert isinstance(res["humidity"], float)

    def test_present_measure_or_na(self, station):
        res = station.present_measure_or_na()

        assert isinstance(res["temperature"], (float, str))
        assert isinstance(res["humidity"], (float, str))

    def test_logging_running(self, station):
        original_state = station.measurement_logger.is_logging()
        try:
            # force test internal start/stop interface
            station.measurement_logger.stop_logging()
            station.measurement_logger.stop_logging()
            assert not station.measurement_logger.is_logging()

            station.measurement_logger.start_logging()
            station.measurement_logger.start_logging()
            assert station.measurement_logger.is_logging()

            # test set interface
            station.measurement_logger.set_log_in_background(False)
            assert not station.measurement_logger.is_logging()
            
            station.measurement_logger.set_log_in_background(True)
            assert station.measurement_logger.is_logging()
            
        # reapply the previous config value
        finally:
            station.measurement_logger.set_log_in_background(original_state)

    def test_logging(self, station):
        original_state = station.measurement_logger.is_logging()
        try:
            station.measurement_logger.set_log_in_background(True)
            sleep(2)
            station.measurement_logger.set_log_in_background(False)
            old_mes = Measurement.fetch_latest()
            assert old_mes is not None
            old_time = old_mes.time

            sleep(1)
            station.measurement_logger.set_log_in_background(True)
            sleep(1)
            
            new_mes = Measurement.fetch_latest()
            assert new_mes is not None
            new_time = new_mes.time
        finally:
            station.measurement_logger.set_log_in_background(original_state)

        assert old_time < new_time
    
    def test_set_logging_interval(self, station):
        """
        Setting a new background measurement interval should result
        in an immediate change (don't want to be stuck)
        """
        original_state = station.measurement_logger.is_logging()
        original_interval = station.measurement_logger.get_logging_interval()
        try:
            station.measurement_logger.set_log_in_background(True)
            station.measurement_logger.set_logging_interval(60)
            sleep(3)
            first_mes = Measurement.fetch_latest()
            
            station.measurement_logger.set_logging_interval(5)
            sleep(3)
            second_mes = Measurement.fetch_latest()
            
            sleep(5)
            third_mes = Measurement.fetch_latest()
            
        finally:
            # reapply the previous config value
            station.measurement_logger.set_log_in_background(original_state)
            station.measurement_logger.set_logging_interval(original_interval)
        
        assert first_mes is not None
        assert second_mes is not None
        assert third_mes is not None
        
        assert first_mes.time < second_mes.time
        assert second_mes.time < third_mes.time
        


    C_TO_F_DATA = [
        (0, 32.0),
        (100, 212.0),
        (-40, -40.0),
        (20, 68.0),
        (37, 98.6)
    ]
    # static methods
    @pytest.mark.parametrize("celsius,fahrenheit", C_TO_F_DATA)
    def test_conversions(self, station, celsius, fahrenheit):
        c_result = station.f_to_celsius(fahrenheit)
        assert celsius == c_result

        f_result = station.c_to_fahrenheit(celsius)
        assert fahrenheit == f_result
