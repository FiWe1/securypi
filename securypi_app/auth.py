import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from securypi_app.sqlite_db.db import register_user, fetch_user_meta_by_id, fetch_user_profile_by_name


bp = Blueprint("auth", __name__, url_prefix="/auth")


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
            success, message = register_user(username, password, is_admin)
            if success:
                return redirect(url_for("auth.login"))
            else:
                error = message

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        profile = fetch_user_profile_by_name(username)
        error = None
        if profile is None:
            error = "Incorrect username."
        elif not check_password_hash(profile["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = profile["id"]
            session["username"] = profile["username"]
            return redirect(url_for("index"))

        flash(error)
    # @TODO clear form - after app restart
    return render_template("auth/login.html")


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
        g.user = fetch_user_meta_by_id(user_id)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def is_logged_in():
    return session.get("username") is not None


def login_required(view):
    """
    Decorate view requiring user to be logged in,
    otherwise redirect to login page.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if is_logged_in():
            return view(**kwargs)
        
        return redirect(url_for("auth.login"))

    return wrapped_view


def is_logged_in_admin():
    return is_logged_in() and g.user["is_admin"] == 1


def admin_rights_required(view):
    """ Decorate view to be accessed only by admin. """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if is_logged_in_admin():
            return view(**kwargs)
        return redirect(url_for("index"))

    return wrapped_view
