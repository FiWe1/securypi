from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("camera_control", __name__, url_prefix="/camera_control")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
def index():
    """ Default (inde) route for camera_control blueprint."""
    return render_template("camera_control.html")
