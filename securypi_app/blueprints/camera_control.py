from flask import Blueprint, render_template, redirect, url_for, flash

from securypi_app.services.auth import login_required
from securypi_app.sensors.camera.mycam import MyPicamera2, Quality


### Globals ###
bp = Blueprint("camera_control", __name__, url_prefix="/camera_control")


@bp.route("/start_recording")
@login_required
def start_recording():
    camera = MyPicamera2.get_instance()

    try:
        camera.start_default_recording(
            stream="main",
            encode_quality=Quality.LOW
        )
    except Exception as e:
        print(f"Error starting recording: {e}")
        flash(f"Error starting recording: {e}")

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

@bp.route("/start_motion_capturing")
@login_required
def start_motion_capturing():
    camera = MyPicamera2.get_instance()

    try:
        camera.motion_capturing.set_motion_capturing(True)
    except Exception as e:
        print(f"Error starting motion capturing: {e}")
        flash(f"Error starting motion capturing: {e}")

    return redirect(url_for("camera_control.index"))


@bp.route("/stop_motion_capturing")
@login_required
def stop_motion_capturing():
    camera = MyPicamera2.get_instance()

    try:
        camera.motion_capturing.set_motion_capturing(False)
    except Exception as e:
        print(f"Error stopping motion capturing: {e}")
        flash("Error stopping motion capturing.")

    return redirect(url_for("camera_control.index"))


@bp.route("/")
@login_required
def index():
    camera = MyPicamera2.get_instance()
    is_recording = camera.is_recording()
    is_motion_capturing = camera.motion_capturing.is_motion_capturing()
    """ Default (inde) route for camera_control blueprint."""
    return render_template("camera_control.html",
                           is_recording=is_recording,
                           is_motion_capturing=is_motion_capturing)
