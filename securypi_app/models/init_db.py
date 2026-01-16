import click
from flask import current_app

from . import db, measurement, user
from .user import User
from securypi_app.services.string_parsing import (
    validate_str_username, validate_str_password,
    generate_random_password_formatted, generate_random_password
)


def init_db():
    with current_app.app_context():
        db.create_all()


def read_password_loop() -> str:
    """
    Helper password input loop.
    Returns password in valid length,
    or random password if user gives up.
    """
    while True:
        password_input = input(
            "enter admin password (default if empty ''): "
        )
        if (password_input == ""):
            return generate_random_password_formatted() # less secure, easier
            # return generate_random_password(12)

        error = validate_str_password(password_input)
        if error is None:
            return password_input
        
        else:
            print(f"{error}, try again!")


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

        register_message = ""
        register_question = input(
            "Do you want to register administrator account? (yes) "
        )
        if register_question in ["y", "yes", "ano"]:
            password = read_password_loop()
            
            result, msg = User.register(username="admin",
                                        password=password,
                                        is_admin=True)
            register_message = (
                f"\nRegistered admin user.\nlogin: admin\npassword: {password}"
            ) if result else "\n" + msg

        click.echo(f"Initialized the database.{register_message}")

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
        if user_type == "admin":
            is_admin = True
        else:
            is_admin = False

        error = validate_str_username(username)
        if error is not None:
            return click.echo(error)
        
        if not User.is_username_free(username):
            return click.echo(f"Username '{username}' is already taken!")
        
        error = validate_str_password(password)
        if error is not None:
            return click.echo(error)
        
        _, message = User.register(username, password, is_admin)
        click.echo(message)
