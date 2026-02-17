import os

from flask import Flask

from .blueprints import measurements
from .models import db


def create_app(test_config=None):
    """ Create and configure an instance of the Flask application. """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # a default secret, should be overridden by instance config
        SECRET_KEY="very_complex_and_unpredictable_secret_key",
        # db path: instance folder
        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///" + os.path.join(app.instance_path,
                                        "securypi_app.sqlite")
        ),
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,
            "max_overflow": 5,
            "pool_timeout": 30,
        },
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

    # DATABASE
    # initialize the app with the extension
    db.init_app(app)
    
    # release db.session on session close
    @app.teardown_appcontext
    def release_db_session(exception=None):
        db.session.remove()

    # CONTEXT PROCESSOR
    # inject into the template context
    from .services.navbar import inject_nav_links, inject_active_page
    app.context_processor(inject_nav_links)
    app.context_processor(inject_active_page)  # from current request

    # REGISTER BLUEPRINTS
    from .blueprints import (
        errors, auth, overview, recordings, camera_control,
        configure, user_settings
    )
    blueprints = [
        errors.bp, auth.bp, overview.bp, measurements.bp, recordings.bp,
        camera_control.bp, configure.bp, user_settings.bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)

    # url_for("index") = url_for("overview.index")
    # --> overview.index is the root index
    app.add_url_rule("/", endpoint="index")

    from .models.init_db import register_cli_commands
    register_cli_commands(app)

    return app
