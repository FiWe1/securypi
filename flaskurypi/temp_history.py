from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("temp_history", __name__, url_prefix="/temp_history")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
def index():
    """ Default (inde) route for temp_history blueprint."""
    return render_template("temp_history.html")
