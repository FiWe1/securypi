from flask import Blueprint
from flask import render_template

from flaskurypi.auth import login_required


### Globals ###
bp = Blueprint("camera_control", __name__, url_prefix="/camera_control")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
@login_required
def index():
    """ Default (inde) route for camera_control blueprint."""
    return render_template("camera_control.html")
