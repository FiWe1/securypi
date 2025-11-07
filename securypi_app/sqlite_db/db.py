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


"""
https://flask.palletsprojects.com/en/stable/tutorial/database/
#
g is a special object that is unique for each request.
It is used to store data that might be accessed by multiple
functions during the request.
The connection is stored and reused instead of creating a new connection
if get_db is called a second time in the same request.

current_app is another special object that points to the Flask application
handling the request.
Since you used an application factory, there is no application object
when writing the rest of your code.
get_db will be called when the application has been created
and is handling a request, so current_app can be used.

sqlite3.connect() establishes a connection to the file
pointed at by the DATABASE configuration key.
This file doesn't have to exist yet, and won't
until you initialize the database later.

sqlite3.Row tells the connection to return rows that behave like dicts.
This allows accessing the columns by name.
"""

def close_db(e=None):
    """
    Removes database from g context.
    Closes the database.
    Must recieve one positional argument.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


"""
https://flask.palletsprojects.com/en/stable/tutorial/database/
#
open_resource() opens a file relative to the securypi_app package,
which is useful since you won't necessarily know
where that location is when deploying the application later.
get_db returns a database connection, which is used
to execute the commands read from the file.
"""
def init_db():
    db = get_db()

    with current_app.open_resource('sqlite_db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# Define a CLI command 'init-db'
@click.command('init-db')
def init_db_command():
    """
    Clears the existing data and create new tables.
    Creates first admin user with:
    login:      admin
    password:   admin4321
    
    Use: flask --app securypi_app init-db
    
    It needs to be added to the app (function init_app())
    """
    init_db()
    # can not call click wrapped function
    register_user("admin", "admin4321", "admin")
    
    click.echo('Initialized the database.\n Default user \'admin\' with password: \'admin4321\'')


def register_user(username, password, user_type='standard', hash_method='pbkdf2:sha256'):
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
        return False, f'User {username} is already registered.'
    else:
        return True, f'Successfully registered {username}.'


@click.command('register-user')
@click.argument('username')
@click.argument('password')
@click.argument('user_type')
def register_user_command(username, password, user_type):
    """ 
    Registers a new user using command line 
    Use: flask --app securypi_app register-user [username] [password]
            [user_type = 'admin' / 'standard']
    
    It needs to be added to the app (function init_app())
    """
    _, message = register_user(username, password, user_type)
    click.echo(message)


"""
https://flask.palletsprojects.com/en/stable/tutorial/database/
#
The call to sqlite3.register_converter() tells Python
how to interpret timestamp values in the database. 
We convert the value to a datetime.datetime.
"""
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    """ Does registration of db functions in app. """
    # tells Flask to call that function when cleaning up after returning the response
    app.teardown_appcontext(close_db)
    
    # adds a new command that can be called with the flask command in CLI
    app.cli.add_command(init_db_command)
    app.cli.add_command(register_user_command)