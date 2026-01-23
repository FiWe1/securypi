from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, jsonify, redirect, url_for

from securypi_app.services.auth import login_required
from securypi_app.models.measurement import Measurement
from securypi_app.peripherals.measurements.weather_station import WeatherStation
from securypi_app.services.app_config import AppConfig


### Globals ###
bp = Blueprint("measurements", __name__, url_prefix="/measurements")


@bp.route("/data")
@login_required
def data():
    # optimalisation: fetching local timezone only once here
    config = AppConfig.get()
    local_timezone = ZoneInfo(config.measurements.geolocation.timezone)

    measurements = Measurement.fetch_previous_range(datetime.now(timezone.utc))
    data = {
        "time": [], "temp": [], "hum": [], "pres": []
    }
    for mes in measurements:
        data["time"].append(mes.time_local_timezone(
            local_timezone).isoformat())
        if mes.temperature is not None:
            data["temp"].append(mes.temperature)
        if mes.humidity is not None:
            data["hum"].append(mes.humidity)
        if mes.pressure is not None:
            data["pres"].append(mes.pressure)

    return jsonify(data)


@bp.route("/")
@login_required
def index():
    """ Default (index) route for measurements blueprint. """
    # init WeatherStation to start logging
    weather_station = WeatherStation.get_instance()

    config = AppConfig.get()
    logging_rate_sec = config.measurements.weather_station.logging_interval_sec

    # cli measurements test
    # last24 = map(Measurement.to_local_timezone,
    #              Measurement.fetch_previous_range(days_before=1))
    # for m in last24:
    #     print(m)

    return render_template(
        "measurements.html",
        logging_rate_sec=logging_rate_sec
    )
