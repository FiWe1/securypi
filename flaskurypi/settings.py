from flask import Blueprint
from flask import render_template

from flaskurypi.auth import login_required, admin_rights_required


### Globals ###
bp = Blueprint("settings", __name__, url_prefix="/settings")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
@login_required
@admin_rights_required
def index():
    """ Default (inde) route for settings blueprint."""
    return render_template("settings.html")


"""
TODO():
set overview camera resolution for picture, video 
set temp logging interval
"""