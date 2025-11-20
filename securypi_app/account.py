from flask import Blueprint
from flask import render_template

from securypi_app.services.auth import login_required

### Globals ###
bp = Blueprint("account", __name__, url_prefix="/account")


@bp.route("/")
@login_required
def index():
    """ Default (inde) route for account blueprint."""
    return render_template("account.html")
