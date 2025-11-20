from flask import Blueprint
from flask import render_template

from securypi_app.services.auth import login_required

### Globals ###
bp = Blueprint("user_settings", __name__, url_prefix="/user_settings")


@bp.route("/")
@login_required
def index():
    """ Default (inde) route for user_settings blueprint."""
    return render_template("user_settings.html")

''' @TODO {
    user preferences configuration:
    - temperature unit (C/F)
    - ...
'''