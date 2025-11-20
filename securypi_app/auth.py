from flask import (
    Blueprint, flash, redirect, render_template, url_for, session, g, request
)
from werkzeug.security import check_password_hash

from securypi_app.models.user import User
from securypi_app.services.auth import logged_out_required


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_user():
    """ 
    Every request retrieves information about the logged in user.
    (logged in user id is stored in session)
    Retrieved data is stored in global (visibility) g context.
    It has the same lifetime as the application context.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.get_meta_by_id(user_id)._mapping


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@bp.route("/login", methods=("GET", "POST"))
@logged_out_required
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.get_by_username(username)
        error = None
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))

        flash(error)
    # @TODO clear form - after app restart
    return render_template("auth/login.html")


# @TODO clear? - not enabling register
# @bp.route("/register", methods=("GET", "POST"))
def register_form():
    """
    Handle the admin registration of a new user.

    Displays the registration form on GET and processes submitted
    credentials on POST.
    """

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        is_admin = request.form["is_admin"]
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            success, message = User.register(username, password, is_admin)
            if success:
                return redirect(url_for("auth.login"))
            else:
                error = message

        flash(error)

    return render_template("auth/register.html")
