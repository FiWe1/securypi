from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("account", __name__, url_prefix="/account")
# url_prefix for routing, subroutes stay relative to this


@bp.route("/")
def index():
    """ Default (inde) route for account blueprint."""
    return render_template("account.html")
