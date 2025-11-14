# source:
# https://flask.palletsprojects.com/en/stable/tutorial/database/

import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash
import click
from flask import current_app, g


# ~request -> get_db() -> g.db (-> ~another_request) -> 
# ~~response -> close_db()
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Closes and removes database from g context.
    Must recieve one positional argument.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('sqlite_db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# Define a CLI command 'init-db'
@click.command('init-db')
def init_db_command():
    """
    CLI command to clear the existing data and create new tables.
    Creates first admin user with:
    login:      admin
    password:   admin4321
    
    Use: flask --app securypi_app init-db
    """
    init_db()
    # can not call click wrapped function
    register_user("admin", "admin4321", "admin")
    
    click.echo("Initialized the database.\n"
               "Default user named: \'admin\' with password: \'admin4321\'")


def register_user(
    username, password, user_type='standard', hash_method='pbkdf2:sha256'):
    """
    Registers a new user. 
    -> (True, "succes")
    -> (False, "user already registered")
    """
    db = get_db()
    try:
        db.execute(
            "INSERT INTO user (username, password, is_admin) VALUES (?, ?, ?)",
            (username, generate_password_hash(password, method=hash_method),
            1 if user_type == 'admin' else 0)
        )
        db.commit()
    except db.IntegrityError:
        return False, f"User {username} is already registered."
    else:
        return True, f"Successfully registered {username}."


@click.command('register-user')
@click.argument('username')
@click.argument('password')
@click.argument('user_type')
def register_user_command(username, password, user_type):
    """ 
    CLI command to register a new user.
    Use: flask --app securypi_app register-user [username] [password]
            [user_type = 'admin' / 'standard']
    """
    _, message = register_user(username, password, user_type)
    click.echo(message)


# Tells Python how to interpret timestamp values in the database
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    """
    Cleans up the database and
    registers cli commands to the app.
    """
    app.teardown_appcontext(close_db)
    
    app.cli.add_command(init_db_command)
    app.cli.add_command(register_user_command)