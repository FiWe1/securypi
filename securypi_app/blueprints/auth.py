from time import sleep

from flask import (
    Blueprint, flash, redirect, render_template, url_for, session, g, request
)

from securypi_app.models.user import User
from securypi_app.services.auth import validate_login, logged_out_required
from securypi_app.services.string_parsing import (
    validate_str_username, validate_str_password
)


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

    if user_id is not None:
        user_row = User.get_meta_by_id(user_id)
        if user_row is not None:
            g.user = user_row._mapping # success
            return
    
    g.user = None # fail

@bp.route("/logout")
def logout():
    session.clear()
    print(f"User '{g.user['username']}' has logged out.")
    
    return redirect(url_for("index"))


@bp.route("/login", methods=("GET", "POST"))
@logged_out_required
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # validate input
        error = None
        error = validate_str_username(username)
        if error is None:
            error = validate_str_password(password)
        
        # authenticate user
        if error is None:
            user, error = validate_login(username, password)

        if error is None and user is not None:
            # login successful
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            
            print(f"User '{username}' has successfully logged in.")
            return redirect(url_for("index"))
        
        if error is not None:
            print(f"User '{username}' login attempt failed:\n{error}.")
            flash(error)
        sleep(1.5) # restrict brute force
    return render_template("auth/login.html")


# not enabling register for now
# @bp.route("/register", methods=("GET", "POST"))
def register():
    """
    Handle the admin registration of a new user.

    Displays the registration form on GET and processes submitted
    credentials on POST.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        is_admin = True if request.form["is_admin"] == "True" else False
        error = None
        error = validate_str_username(username)
        if error is None:
            error = validate_str_password(password)
        
        if not User.is_username_free(username):
            error = f"Username '{username}' is already taken!"

        if error is None:
            success, message = User.register(username, password, is_admin)
            if success:
                return redirect(url_for("auth.login"))
            else:
                error = message

        flash(error)

    return render_template("auth/register.html")
