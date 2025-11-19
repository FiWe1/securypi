from flask import Response, Blueprint, render_template, request, url_for
# from flask import render_template_string, flash, g, redirect, flash, current_app
# from werkzeug.exceptions import abort

from securypi_app.auth import login_required

from securypi_app.sensors import mycam
from securypi_app.sensors import temphum


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
    camera = mycam.MyPicamera2.get_instance()
    output = mycam.StreamingOutput()

    camera.start_capture_stream(output)
    return Response(mycam.generate_frames(output),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@bp.route("/picture.jpg")
@login_required
def picture_feed():
    """ Route for a single snapshot. """
    camera = mycam.MyPicamera2.get_instance()
    try:
        camera.stop_capture_stream()

        jpeg_data = camera.capture_picture()
        return Response(jpeg_data, mimetype="image/jpeg")

    except Exception as e:
        print(f"Error capturing picture: {e}")
        return Response(status=500)


@bp.route("/stop_camera", methods=["POST"])
@login_required
def stop_video_feed():
    camera = mycam.MyPicamera2.get_instance()
    camera.stop_capture_stream()
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
    temperature_unit = "C"
    temperature, humidity = temphum.measure_temp_hum(
        temperature_unit=temperature_unit)
    if temperature is None or humidity is None:
        temperature = "N/A"
        humidity = "N/A"

    # Determine the template and URL for the <img> tag based on the mode
    if mode == "stream":
        img_src = url_for("overview.video_feed")
    else:  # Default is "picture"
        img_src = url_for("overview.picture_feed")

    return render_template("overview/index.html",
                           mode=mode,
                           img_src=img_src,
                           temperature=temperature,
                           humidity=humidity,
                           temperature_unit=temperature_unit)
