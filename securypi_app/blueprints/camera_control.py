from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash

from securypi_app.services.auth import login_required
from securypi_app.sensors.mycam import MyPicamera2, Quality


### Globals ###
bp = Blueprint("camera_control", __name__, url_prefix="/camera_control")


@bp.route("/start_recording")
@login_required
def start_recording():
    camera = MyPicamera2.get_instance()
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    path = "recording_demo/"
    full_path = path + filename

    try:
        camera.start_recording_to_file(full_path,
                                       stream="main",
                                       encode_quality=Quality.LOW)
    except Exception as e:
        print(f"Error starting recording: {e}")
        flash("Error starting recording.")

    return redirect(url_for("camera_control.index"))


@bp.route("/stop_recording")
@login_required
def stop_recording():
    camera = MyPicamera2.get_instance()

    try:
        camera.stop_recording_to_file()
    except Exception as e:
        print(f"Error stopping recording: {e}")
        flash("Error stopping recording.")

    return redirect(url_for("camera_control.index"))


@bp.route("/")
@login_required
def index():
    camera = MyPicamera2.get_instance()
    is_recording = camera.is_recording()
    """ Default (inde) route for camera_control blueprint."""
    return render_template("camera_control.html",
                           is_recording=is_recording)
