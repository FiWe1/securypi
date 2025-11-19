import click
from flask import current_app

from . import db, measurement, user
from .user import User


def init_db():
    with current_app.app_context():
        db.create_all()


def register_cli_commands(app):

    @app.cli.command("init-db")
    def init_db_command():
        """
        CLI command to clear the existing data and create new tables.
        Creates first admin user with:
        login:      admin
        password:   admin4321

        Use: flask --app securypi_app init-db
        """
        init_db()
        User.register("admin", "admin4321", "admin")

        click.echo("Initialized the database.\n"
                   "Default user named: \'admin\' with password: \'admin4321\'")

    @app.cli.command("register-user")
    @click.argument("username")
    @click.argument("password")
    @click.argument("user_type")
    def register_user_command(username, password, user_type):
        """ 
        CLI command to register a new user.
        Use: flask --app securypi_app register-user [username] [password]
                [user_type = 'admin' / 'standard']
        """
        _, message = User.register(username, password, user_type)
        click.echo(message)
