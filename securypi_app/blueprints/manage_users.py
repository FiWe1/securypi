from flask import (
    Blueprint, render_template, request, flash, session, redirect, url_for
)

from securypi_app.models.user import User
from securypi_app.services.auth import (
    login_required, admin_rights_required, register_user,
    update_account_details, change_user_password
)
from securypi_app.services.string_parsing import validate_str_username

### Globals ###
bp = Blueprint("manage_users", __name__, url_prefix="/manage_users")


def edit_user_action(user_id,
                     username,
                     email,
                     password,
                     confirm_password,
                     is_admin) -> str:
    """ Update user according to form data, return result message. """
    username_message = validate_str_username(username)
    if username_message is not None:
        return username_message
    
    message = ""
    user = User.get_by_id(user_id)
    if user is None:
        return f"Could not identify user {username}."
    
    if password != "" or confirm_password != "":
        message = change_user_password(user, password, confirm_password)
    message += "\n" + update_account_details(user, username, email, is_admin)
    
    return message


def delete_user_action(username) -> str:
    """ Delete user according to form data, return result message. """
    user = User.get_by_username(username)
    if user is None:
        return f"User with username '{username}' does not exist."
    
    return user.delete()

def handle_form_action(form):
    """ Recieve and handle form data. Refreshes page and flashes result. """
    action = form["action"]
    if action == "add_new_user":
        username = form.get("username")
        password = form.get("new password")
        confirm_password = form.get("confirm password")
        email = form.get("email")
        is_admin = form.get("admin")
        
        # 'on' if checkbox is checked, None otherwise
        email = email if email != "" else None
        is_admin = True if is_admin is not None else False
        
        message = register_user(username,
                                password,
                                confirm_password,
                                is_admin,
                                email)
        
    elif action == "edit_user":
        user_id = form.get("user_id")
        username = form.get("username")
        email = form.get("email")
        password = form.get("new password")
        confirm_password = form.get("confirm password")
        is_admin = form.get("admin")
        
        email = email if email is not None and email != "" else None
        # 'on' if checkbox is checked, None otherwise
        is_admin = True if is_admin is not None else False
        
        message = edit_user_action(user_id,
                                   username,
                                   email,
                                   password,
                                   confirm_password,
                                   is_admin)
        
    elif action == "delete_user":
        username = form.get("username")
        
        message = delete_user_action(username)
    else:
        message = "Unknown form action."
    
    flash(message)
    return redirect(url_for("manage_users.index"))


@bp.route("/", methods=("GET", "POST"))
@login_required
@admin_rights_required
def index():
    """ Default (index) route for manage_users blueprint."""
    if request.method == "POST":
        return handle_form_action(request.form)
    
    users = User.fetch_all()
    current_id = session.get("user_id")
    user_labels = ["user_id", "username", "new password", "confirm password",
        "email", "admin"]
    user_data = [
        {
            "user_id": user.id,
            "username": user.username,
            "new password": "",
            "confirm password": "",
            "email": user.email if user.email is not None else "",
            "admin": user.is_admin
        }
        for user in users if user.id != current_id
    ]
    return render_template("manage_users.html",
                           user_labels=user_labels,
                           user_data=user_data)
