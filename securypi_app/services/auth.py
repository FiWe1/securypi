"""
Utility functions as a service around authentication.
"""

import functools

from flask import (
    redirect, url_for, g, session
)
from werkzeug.security import check_password_hash

from securypi_app.models.user import User


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


def logged_out_required(view):
    """
    Decorate view preventing logged user to enter the route,
    redirecting to home page.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not is_logged_in():
            return view(**kwargs)

        return redirect(url_for("index"))

    return wrapped_view


def is_logged_in_admin():
    return (
        is_logged_in()
        and g.user is not None
        and g.user["is_admin"] == True
    )


def admin_rights_required(view):
    """ Decorate view to be accessed only by admin. """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if is_logged_in_admin():
            return view(**kwargs)
        return redirect(url_for("index"))

    return wrapped_view


def validate_login(username, password) -> tuple[User | None, str | None]:
    """
    Compare login information against database.
    Valid:   -> User(), None
    Invalid: -> None, "Error message"
    """
    user = User.get_by_username(username)
    error = None
    if user is None:
        error = "Incorrect username."
    elif not check_password_hash(user.hashed_password, password):
        error = "Incorrect password."
        user = None
    
    return user, error