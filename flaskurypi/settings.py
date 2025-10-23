from flask import Blueprint
from flask import render_template

from flaskurypi.auth import login_required


### Globals ###
bp = Blueprint("settings", __name__, url_prefix="/settings")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
@login_required
def index():
    """ Default (inde) route for settings blueprint."""
    return render_template("settings.html")
