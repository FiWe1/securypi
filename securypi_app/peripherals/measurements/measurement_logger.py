from time import sleep
from threading import Thread, Event


# @TODO move to centralised serialised json config
LOGGING_INTERVAL_SEC = 30
LOG_WEATHER_IN_BACKGROUND = True


class MeasurementLogger():
    
    def __init__(self, weather_station):
        self._weather_station = weather_station
        
        # background logging
        self._log_in_background = False
        self._logging_thread = None
        self._logging_stop_event = Event()
        self.apply_logging_config()
    
    def logger(self):
        """
        Countinuously log sensor measurements to the database
        in configured interval.
        """
        # The new thread needs app context in order to have access
        # to app variables, access to database
        sleep(0.1) # avoid too many read requests at app start
        with self._weather_station._app.app_context():
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
        log = LOG_WEATHER_IN_BACKGROUND
        log_sec = LOGGING_INTERVAL_SEC
        
        self.set_logging_interval(log_sec)
        self.set_log_in_background(log)

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
