from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("settings", __name__, url_prefix="/settings")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
def index():
    """ Default (inde) route for settings blueprint."""
    return render_template("settings.html")
