from flask import (
    Blueprint, request, Response, render_template, send_from_directory, current_app, flash,
    redirect, url_for
)

from securypi_app.services.auth import login_required
from securypi_app.services.captures import (
    list_motion_captures, motion_captures_absolute_path, is_motion_capture_valid,
    list_recordings, recordings_absolute_path, is_recording_valid,
    delete_motion_captures, delete_recordings, create_zip_stream
)
from securypi_app.services.auth import is_logged_in_admin


### Globals ###
bp = Blueprint("recordings", __name__, url_prefix="/recordings")


@bp.route("/download_motion_capture/<filename>")
def download_motion_capture(filename):
    directory = motion_captures_absolute_path(current_app.root_path)
    if is_motion_capture_valid(filename):
        return send_from_directory(directory, filename, as_attachment=True)

    flash(f"Invalid filename: {filename}")
    return redirect(url_for("recordings.index"))


@bp.route("/download_recording/<filename>")
def download_recording(filename):
    directory = recordings_absolute_path(current_app.root_path)
    if is_recording_valid(filename):
        return send_from_directory(directory, filename, as_attachment=True)

    flash(f"Invalid filename: {filename}")
    return redirect(url_for("recordings.index"))


def handle_batch_form_action(form):
    action = form.get("action")

    motion_captures = list_motion_captures()
    recordings = list_recordings()

    selected_motion_captures = [motion for motion in motion_captures
                                if form.get(motion) is not None]
    selected_recordings = [rec for rec in recordings
                           if form.get(rec) is not None]

    # only admin can delete
    if action == "delete_selected" and is_logged_in_admin():
        delete_motion_captures(selected_motion_captures)
        delete_recordings(selected_recordings)

    elif action == "download_selected":
        zip_stream = create_zip_stream(selected_motion_captures, selected_recordings)
        return Response(
            zip_stream,
            mimetype="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=selected_captures.zip",
            }
        )

    return redirect(url_for("recordings.index"))


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ Default (index) route for recordings blueprint. """
    if request.method == "POST":
        return handle_batch_form_action(request.form)

    motion_captures = list_motion_captures()
    recordings = list_recordings()

    return render_template("recordings.html",
                           motion_captures=motion_captures,
                           recordings=recordings)
