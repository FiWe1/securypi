from flask import Blueprint
from flask import render_template

from securypi_app.auth import login_required, admin_rights_required


### Globals ###
bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/")
@login_required
@admin_rights_required
def index():
    """ Default (index) route for settings blueprint. """
    return render_template("settings.html")


"""
@TODO {
set overview camera resolution for picture, video 
set temp logging interval
}
"""
