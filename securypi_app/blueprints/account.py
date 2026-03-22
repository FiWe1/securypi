from flask import (
    Blueprint, render_template, request, flash, session, redirect, url_for
)

from securypi_app.models.user import User
from securypi_app.models.notification_prefs import NotificationPrefs
from securypi_app.services.auth import (
    login_required, verify_change_user_password, update_account_details
)
from securypi_app.services.notifications import parse_save_notification_prefs


### Globals ###
bp = Blueprint("account", __name__, url_prefix="/account")


def handle_form_action(form, user_id):
    action = form["action"]
    if action == "change_password":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        new_password_again = request.form["new_password_again"]

        message = verify_change_user_password(current_password,
                                              new_password,
                                              new_password_again)
        flash(message)
    elif action == "update_account_details":
        username = form.get("username")
        email = form.get("email")

        username = username if username is not None and username != "" else None
        email = email if email is not None and email != "" else None
        user = User.get_by_id(user_id)
        message = update_account_details(user=user,
                                         username=username,
                                         email=email)
        flash(message)
    elif action == "update_notifications":
        prefs = NotificationPrefs.get_or_create(user_id)
        error = parse_save_notification_prefs(prefs, form)
        if error:
            flash(error)
        else:
            flash("Notification preferences saved.")
    return redirect(url_for("account.index"))


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """ Default (index) route for account blueprint."""
    user_id = session.get("user_id")
    if request.method == "POST":
        return handle_form_action(request.form, user_id)

    user = User.get_by_id(user_id)
    account_details = user.account_details()
    prefs = NotificationPrefs.get_or_create(user_id)
    return render_template("account.html",
                           account_details=account_details,
                           prefs=prefs,
                           user_email=user.email if user else None)
