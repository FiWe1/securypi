from flask import Blueprint
from flask import render_template

from securypi_app.services.auth import login_required, admin_rights_required


### Globals ###
bp = Blueprint("configuration", __name__, url_prefix="/configuration")


@bp.route("/")
@login_required
@admin_rights_required
def index():
    """ Default (index) route for configuration blueprint. """
    return render_template("configuration.html")


"""
@TODO {
    CREATE CONFIG DATABASE
set username and password length requirements (get them in string_parsing)
set overview camera resolution for picture, video 
set temp logging interval
}
"""
