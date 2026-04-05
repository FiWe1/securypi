import logging

from flask import (
    Response, Blueprint, render_template, request, url_for, jsonify
)

from securypi_app.services.auth import login_required, api_login_required

from securypi_app.peripherals.camera.mycam import MyPicamera2
from securypi_app.peripherals.measurements.weather_station import WeatherStation

logger = logging.getLogger(__name__)

MEASUREMENTS_REFRESH_SEC = 30


### Globals ###
bp = Blueprint("overview", __name__)  # no url_prefix, main overview page


@bp.route("/stream.mjpeg")
@api_login_required
def video_feed():
    """ Route returns mjpeg stream - continuous img stream. """
    try:
        camera = MyPicamera2.get_instance()
        streaming_output = camera.streaming.start_capture_stream()
        
        return Response(streaming_output.generate_frames(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        logger.error("Error during startup of mjpeg stream: %s", e)
        return Response(status=500)


@bp.route("/picture.jpg")
@api_login_required
def picture_feed():
    """ Route returns single jpeg snapshot. """
    try:
        camera = MyPicamera2.get_instance()
        jpeg_data = camera.capture_picture()
        return Response(jpeg_data, mimetype="image/jpeg")
    
    except Exception as e:
        logger.error("Error capturing picture: %s", e)
        return Response(status=500)


@bp.route("/current_measurements")
@api_login_required
def current_measurements():
    """ Return current measurements from sensors for visualisation as json. """
    sensor = WeatherStation.get_instance()
    measurements = sensor.present_measure_or_na()
    return jsonify(measurements)


@bp.route("/", methods=["GET"])
@login_required
def index():
    """
    Main overview page showing either live stream or snapshot based on mode,
    together with measurements.
    """
    measurements_refresh_sec = MEASUREMENTS_REFRESH_SEC

    sensor = WeatherStation.get_instance()
    measurements = sensor.present_measure_or_na()

    # get the desired mode from the request (default to "picture")
    mode = request.args.get("mode", "picture")

    # determine the template and URL for the <img> tag based on the mode
    if mode == "stream":
        camera_feed_src = url_for("overview.video_feed")
    else:  # Default is "picture"
        camera_feed_src = url_for("overview.picture_feed")

    return render_template(
        "overview/index.html",
        mode=mode,
        camera_feed_src=camera_feed_src,
        measurements=measurements,
        measurements_refresh_sec=measurements_refresh_sec
    )
