from flask import Blueprint
from flask import render_template

from securypi_app.auth import login_required


### Globals ###
bp = Blueprint("temp_history", __name__, url_prefix="/temp_history")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
@login_required
def index():
    """ Default (inde) route for temp_history blueprint."""
    return render_template("temp_history.html")
