from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("recordings", __name__, url_prefix="/recordings")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
def index():
    """ Default (inde) route for recordings blueprint."""
    return render_template("recordings.html")
