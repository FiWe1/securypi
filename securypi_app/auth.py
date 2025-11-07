import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from securypi_app.sqlite_db.db import get_db, register_user


bp = Blueprint('auth', __name__, url_prefix='/auth')


# not enabling register
# @bp.route('/register', methods=('GET', 'POST'))
def register_form():
    """
    Route for registering a new user by admin.
    Depends on sqlite_db.db.register_user
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form['is_admin']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            success, message = register_user(username, password, is_admin)
            if success:
                return redirect(url_for("auth.login"))
            else:
                error = message

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    # TODO(clear form - after app restart)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


"""
This decorator returns a new view function that wraps the original view it’s applied to.
The new function checks if a user is loaded and redirects to the login page otherwise.
If a user is loaded the original view is called and continues normally.
You’ll use this decorator when writing the blog views
"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


""" Decorate view to be accessed only by admin. """
def admin_rights_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None and g.user["is_Admin"] == 1:
            return view(**kwargs)

        return redirect(url_for('index'))

    return wrapped_view