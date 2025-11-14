from flask import Blueprint
from flask import render_template

from securypi_app.auth import login_required


### Globals ###
bp = Blueprint("recordings", __name__, url_prefix="/recordings")


@bp.route("/")
@login_required
def index():
    """ Default (index) route for recordings blueprint. """
    return render_template("recordings.html")
