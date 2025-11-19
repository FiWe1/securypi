import os
import logging  # @TODO logging

from flask import Flask, request, url_for, current_app
from .models import db


# @TODO move to another module)
def inject_active_page():
    return {"active_page": url_for(request.endpoint)}


def create_app(test_config=None):
    """ Create and configure an instance of the Flask application. """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # a default secret, should be overridden by instance config
        SECRET_KEY="very_complex_and_unpredictable_secret_key",
        # db path: instance folder
        SQLALCHEMY_DATABASE_URI= (
            "sqlite:///" + os.path.join(app.instance_path,
                                        "securypi_app.sqlite")
        )
    )

    if test_config is None:
        # @TODO instance config
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ###
    # LOGGING
    #
    # @TODO Logging)
    # # app log file in the instance folder
    # log_path = os.path.join(app.instance_path, "app.log")
    # logging.basicConfig(
    #     filename=log_path,
    #     level=logging.INFO,
    #     format="%(asctime)s %(levelname)s: %(message)s 
    # ...[in %(pathname)s:%(lineno)d]"
    # )

    # DATABASE
    # initialize the app with the extension
    db.init_app(app)

    # CONTEXT PROCESSOR
    # inject into the template context
    from . import navbar
    app.context_processor(navbar.inject_nav_links)
    app.context_processor(inject_active_page)  # from current request

    # REGISTER BLUEPRINTS
    from . import (
        auth, overview, temp_history, recordings,camera_control,
        settings, account
    )

    blueprints = [
        auth.bp, overview.bp, temp_history.bp, recordings.bp,
        camera_control.bp, settings.bp, account.bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)

    # make url_for("index") == url_for("overview.index")
    # -- overview.index is the main index
    app.add_url_rule("/", endpoint="index")

    from .models.init_db import register_cli_commands
    register_cli_commands(app)

    return app
