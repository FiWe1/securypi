from flask import Blueprint
from flask import render_template

from securypi_app.services.auth import login_required, admin_rights_required


### Globals ###
bp = Blueprint("configure", __name__, url_prefix="/configure")


@bp.route("/")
@login_required
@admin_rights_required
def index():
    """ Default (index) route for configure blueprint. """
    return render_template("configure.html")


"""
@TODO {
    CREATE CONFIG DATABASE
set username and password length requirements (get them in string_parsing)
set overview camera resolution for picture, video 
set temp logging interval
}
"""
