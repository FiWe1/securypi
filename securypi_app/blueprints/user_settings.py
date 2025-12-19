from flask import Blueprint, render_template, request, flash, g

from securypi_app.models.user import User
from securypi_app.services.auth import login_required, validate_login
from securypi_app.services.string_parsing import validate_str_password

### Globals ###
bp = Blueprint("user_settings", __name__, url_prefix="/user_settings")


''' @TODO {
    user preferences configuration:
    - temperature unit (C/F)
    - ...
'''


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """ Default (index) route for user_settings blueprint."""
    # change password
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        new_password_again = request.form["new_password_again"]
        
        user, old_password_error = (
            validate_login(g.user["username"], current_password)
        )
        new_password_error = validate_str_password(new_password)
    
        if old_password_error is not None:
            flash(old_password_error)
        elif new_password_error is not None:
            flash(new_password_error)
        elif new_password != new_password_again:
            flash("Passwords do not match!")
        else:
            result, mes = user.change_password(new_password)
            flash(mes)
        
    return render_template("user_settings.html")
