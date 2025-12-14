from flask import Blueprint, render_template, redirect, url_for

from securypi_app.services.auth import login_required
from securypi_app.models.measurement import Measurement
from securypi_app.peripherals.measurements.weather_station import WeatherStation


### Globals ###
bp = Blueprint("temp_history", __name__, url_prefix="/temp_history")


@bp.route("/")
@login_required
def index():
    """ Default (index) route for temp_history blueprint. """
    # init WeatherStation to start logging
    weather_station = WeatherStation.get_instance()
    
    # cli measurements test
    last24 = map(Measurement.to_local_timezone,
                 Measurement.fetch_previous_range(days_before=1))
    for m in last24:
        print(m)
    
    return render_template("temp_history.html")
