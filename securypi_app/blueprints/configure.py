from flask import Blueprint, render_template, redirect, url_for, flash

from securypi_app.services.auth import login_required, admin_rights_required
from securypi_app.peripherals.measurements.weather_station import WeatherStation


### Globals ###
bp = Blueprint("configure", __name__, url_prefix="/configure")


@bp.route("/start_weather_logging")
@login_required
def start_weather_logging():
    sensor = WeatherStation.get_instance()

    try:
        sensor.measurement_logger.set_log_in_background(True)
    except Exception as e:
        print(f"Error starting recording: {e}")
        flash("Error starting recording.")

    return redirect(url_for("configure.index"))


@bp.route("/stop_weather_logging")
@login_required
def stop_weather_logging():
    sensor = WeatherStation.get_instance()

    try:
        sensor.measurement_logger.set_log_in_background(False)
    except Exception as e:
        print(f"Error stopping recording: {e}")
        flash("Error stopping recording.")

    return redirect(url_for("configure.index"))


@bp.route("/")
@login_required
@admin_rights_required
def index():
    """ Default (index) route for configure blueprint. """
    sensor = WeatherStation.get_instance()
    is_weather_logging = sensor.measurement_logger.is_logging()
    return render_template("configure.html",
                           is_weather_logging=is_weather_logging)


"""
@TODO {
    CREATE CONFIG DATABASE
set username and password length requirements (get them in string_parsing)
set overview camera resolution for picture, video 
set temp logging interval
}
"""
