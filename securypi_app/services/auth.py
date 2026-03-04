"""
Utility functions as a service around authentication.
"""

import functools

from flask import (
    redirect, url_for, g, session
)
from werkzeug.security import check_password_hash

from securypi_app.models.user import User
from securypi_app.services.string_parsing import (
    validate_str_password, validate_str_username, is_email_valid
)


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


def verify_change_user_password(current_password,
                                new_password,
                                new_password_again) -> str:
    """
    Verify and change password of the logged in user.
    Returns result message.
    """
    user, old_password_error = (
            validate_login(g.user["username"], current_password)
        )
    if old_password_error is not None:
        return old_password_error
    
    if user is None:
        return "Could not verify user."
    
    return change_user_password(user, new_password, new_password_again)


def change_user_password(user: User, new_password, new_password_again) -> str:
    new_password_error = validate_str_password(new_password)
    if new_password_error is not None:
        return new_password_error
    
    if new_password != new_password_again:
        return "Passwords do not match!"

    if user is not None:
        _, mes = user.change_password(new_password)
        return mes
    
    return "Failed to verify and change password"


def update_account_details(user: User, username=None, email=None, is_admin=None) -> str:
    """
    Verify passed on user properties and update user account.
    Returns result message.
    """
    update = False
    # update username
    if username is not None and username != user.username:
        valid_username_error = validate_str_username(username)
        if valid_username_error is not None:
            return valid_username_error
        username_free = User.is_username_free(username)
        
        if username_free:
            user.username = username
            update = True
        else:
            return f"Username '{username}' is already taken."
    
    # update email
    if email is not None and email != user.email:
        if is_email_valid(email):
            user.email = email
            update = True
        else:
            return f"Email '{email}' is in invalid format."
    
    # update is_admin
    if is_admin is not None:
        user.is_admin = is_admin
        update = True
    
    # apply update
    if update == True:
        result = user.update()
        if result is None:
            return "Account details successfully updated."
        else:
            return result
    else:
        return "No changes to update."


def register_user(username,
                  password,
                  confirm_password,
                  is_admin=False,
                  email=None) -> str:
    """
    Register a new user with the provided credentials.
    Returns an error message if registration fails, otherwise a success message.
    """
    error = validate_str_username(username)
    if error is not None:
        return error
    
    error = validate_str_password(password)
    if error is not None:
        return error
    if password != confirm_password:
        return "Passwords do not match!"
    
    if email is not None and email != "":
        if not is_email_valid(email):
            return f"Email '{email}' is in invalid format."
    
    if not User.is_username_free(username):
        return f"Username '{username}' is already taken."
    
    _, message = User.register(username=username,
                                    password=password,
                                    is_admin=is_admin,
                                    email=email)
    return message
