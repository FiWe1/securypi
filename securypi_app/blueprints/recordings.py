from flask import (
    Blueprint, render_template, send_from_directory, current_app, flash,
    redirect, url_for
)

from securypi_app.services.auth import login_required
from securypi_app.services.captures import (
    list_motion_captures, motion_captures_full_path, is_motion_capture_valid,
    list_recordings, recordings_full_path, is_recording_valid,
)


### Globals ###
bp = Blueprint("recordings", __name__, url_prefix="/recordings")

@bp.route("/download_motion_capture/<path:filename>")
def download_motion_capture(filename):
    directory = motion_captures_full_path(current_app.root_path)
    if is_motion_capture_valid(filename):
        return send_from_directory(directory, filename, as_attachment=True)
    
    flash(f"Invalid filename: {filename}") # @TODO fix flash style layout
    return redirect(url_for("recordings.index"))


@bp.route("/download_recording/<path:filename>")
def download_recording(filename):
    directory = recordings_full_path(current_app.root_path)
    if is_recording_valid(filename):
        return send_from_directory(directory, filename, as_attachment=True)

    flash(f"Invalid filename: {filename}")
    return redirect(url_for("recordings.index"))



@bp.route("/")
@login_required
def index():
    """ Default (index) route for recordings blueprint. """
    motion_captures = list_motion_captures()
    recordings = list_recordings()
    
    return render_template("recordings.html",
                           motion_captures=motion_captures,
                           recordings=recordings)
