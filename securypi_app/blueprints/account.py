from flask import Blueprint, render_template, request, flash, g

from securypi_app.models.user import User
from securypi_app.services.auth import (
    login_required, verify_change_user_password
)

### Globals ###
bp = Blueprint("account", __name__, url_prefix="/account")


''' @TODO {
    user preferences configuration:
    - temperature unit (C/F)
    - ...
'''


def handle_form_action(form):
    action = form["action"]
    if action == "change_password":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        new_password_again = request.form["new_password_again"]
        
        message = verify_change_user_password(current_password,
                                              new_password,
                                              new_password_again)
        flash(message)

@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """ Default (index) route for account blueprint."""
    if request.method == "POST":
        handle_form_action(request.form)
        
    return render_template("account.html")
