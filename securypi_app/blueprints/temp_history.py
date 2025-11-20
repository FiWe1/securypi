from flask import Blueprint, render_template, redirect, url_for

from securypi_app.services.auth import login_required
from securypi_app.models.measurement import Measurement
from securypi_app.sensors.weather_sensor import WeatherSensor


### Globals ###
bp = Blueprint("temp_history", __name__, url_prefix="/temp_history")


@bp.route("/")
@login_required
def index():
    """ Default (index) route for temp_history blueprint. """
    # test
    Measurement.printall()
    return render_template("temp_history.html")
