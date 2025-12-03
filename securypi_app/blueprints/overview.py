from flask import Response, Blueprint, render_template, request, url_for

from securypi_app.services.auth import login_required

from securypi_app.peripherals.camera.mycam import MyPicamera2
from securypi_app.peripherals.measurements.weather_station import WeatherStation


### Globals ###
bp = Blueprint("overview", __name__)  # no url_prefix, main overview page


@bp.route("/stream.mjpg")
@login_required
def video_feed():
    """
    Video streaming route to the src attribute of an img tag.
    Uses a generator function to stream the response.
    Calls mycam, a picamera2 wrapper class contained in mycam.py
    """
    camera = MyPicamera2.get_instance()
    streaming_output = camera.streaming.start_capture_stream()

    return Response(streaming_output.generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@bp.route("/picture.jpg")
@login_required
def picture_feed():
    """ Route for a single snapshot. """
    camera = MyPicamera2.get_instance()
    try:
        jpeg_data = camera.capture_picture()
        return Response(jpeg_data, mimetype="image/jpeg")

    except Exception as e:
        print(f"Error capturing picture: {e}")
        return Response(status=500)


@bp.route("/stop_camera", methods=["POST"])
@login_required
def stop_video_feed():
    camera = MyPicamera2.get_instance()
    camera.streaming.stop_capture_stream()
    return ("Video feed stopped", 200)


@bp.route("/", methods=["GET"])
@login_required
def index():
    """
    Main overview page showing either live stream or snapshot based on mode,
    together with temperature and humidity readings.
    """

    # Get the desired mode from the request (default to "picture")
    mode = request.args.get("mode", "picture")

    # temperature and humidity sensor @TODO from db)
    temp_unit = "C"  # @TODO from user settings in db
    sensor = WeatherStation.get_instance()
    readings = sensor.present_measure_or_na(temp_unit=temp_unit)

    # Determine the template and URL for the <img> tag based on the mode
    if mode == "stream":
        img_src = url_for("overview.video_feed")
    else:  # Default is "picture"
        img_src = url_for("overview.picture_feed")

    return render_template("overview/index.html",
                           mode=mode,
                           img_src=img_src,
                           temperature=readings["temperature"],
                           humidity=readings["humidity"],
                           pressure=readings["pressure"],
                           temperature_unit=temp_unit)
