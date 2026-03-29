from flask import Blueprint, render_template, redirect, url_for, flash, request

from securypi_app.services.auth import login_required, is_logged_in_admin
from securypi_app.services.camera_control import (
    get_motion_capturing_config, get_recording_config, get_streaming_config,
    update_motion_capturing_config, update_recording_config,
    update_streaming_config
)
from securypi_app.peripherals.camera.mycam import MyPicamera2, Quality
from securypi_app.services.captures import (
    has_enough_free_storage, recordings_path, motion_captures_path
)


### Globals ###
bp = Blueprint("camera_control", __name__, url_prefix="/camera_control")


@bp.route("/start_recording", methods=["POST"])
@login_required
def start_recording():
    camera = MyPicamera2.get_instance()

    if not has_enough_free_storage(recordings_path()):
        message = "Not enough free storage (less than 1 GB). Cannot start recording."
    elif camera.motion_capturing.is_motion_capturing():
        message = (
            "Can't start a recording while "
            "background motion capturing is running."
        )
    else:
        try:
            camera.start_default_recording(
                stream="main",
                encode_quality=Quality.LOW
            )
            message = "Started recording."
        except Exception as e:
            print(f"Error starting recording: {e}")
            message = f"An error occured during starting recording."

    flash(message)
    return redirect(url_for("camera_control.index"))


@bp.route("/stop_recording", methods=["POST"])
@login_required
def stop_recording():
    camera = MyPicamera2.get_instance()

    try:
        camera.stop_recording_to_file()
        message = "Stopped recording."
    except Exception as e:
        print(f"Error stopping recording: {e}")
        message = "An error occured during stopping recording."

    flash(message)
    return redirect(url_for("camera_control.index"))

@bp.route("/start_motion_capturing", methods=["POST"])
@login_required
def start_motion_capturing():
    camera = MyPicamera2.get_instance()

    if not has_enough_free_storage(motion_captures_path()):
        message = "Not enough free storage (less than 1 GB). Cannot start motion capturing."
    elif camera.is_recording():
        message = (
            "Can't start motion capturing while "
            "background recording is running."
        )
    else:
        try:
            camera.motion_capturing.set_motion_capturing(True)
            message = "Started motion capturing."
        except Exception as e:
            print(f"Error starting motion capturing: {e}")
            message = f"An error occured during starting motion capturing."

    flash(message)
    return redirect(url_for("camera_control.index"))


@bp.route("/stop_motion_capturing", methods=["POST"])
@login_required
def stop_motion_capturing():
    camera = MyPicamera2.get_instance()

    try:
        camera.motion_capturing.set_motion_capturing(False)
        message = "Stopped motion capturing."
    except Exception as e:
        print(f"Error stopping motion capturing: {e}")
        message = "An error occured during stopping motion capturing."

    flash(message)
    return redirect(url_for("camera_control.index"))


def handle_form_action(form):
    """ Recieve and handle form data. Refreshes page and flashes result. """
    action = form["action"]
    if action == "update_recording_config":
        current_config = get_recording_config()
        updated_config = {
            key: form.get(key) for key in current_config
        }
        message = update_recording_config(current_config, updated_config)
        
    elif action == "update_streaming_config":
        current_config = get_streaming_config()
        updated_config = {
            key: form.get(key) for key in current_config
        }
        message = update_streaming_config(current_config, updated_config)
    elif action == "update_motion_capturing_config":
        current_config = get_motion_capturing_config()
        updated_config = {
            key: form.get(key) for key in current_config
        }
        message = update_motion_capturing_config(current_config, updated_config)
    else:
        message = "Unknown form action."
        
    flash(message)
    return redirect(url_for("camera_control.index"))


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """ Default (index) route for camera_control blueprint."""
    # configuration form, available only for admin
    if request.method == "POST" and is_logged_in_admin():
        return handle_form_action(request.form)
    
    camera = MyPicamera2.get_instance()
    """ Default (inde) route for camera_control blueprint."""
    return render_template("camera_control.html",
                           is_recording=camera.is_recording(),
                           is_motion_capturing=camera.motion_capturing.is_motion_capturing(),
                           recording_config=get_recording_config(),
                           streaming_config=get_streaming_config(),
                           motion_capturing_config=get_motion_capturing_config())
