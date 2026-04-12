""" Flask server environment variables """

import os
import secrets
from datetime import timedelta

from securypi_app.models.app_config import AppConfig

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# always fresh secret key, never stored
SECRET_KEY = secrets.token_hex(32)

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "securypi_app.sqlite")
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 5,
    "pool_timeout": 30,
}

# permanent session lifetime with expiration set in hours in app_config.json
SESSION_REFRESH_EACH_REQUEST = False
PERMANENT_SESSION_LIFETIME=timedelta(
    hours=AppConfig.get().authentication.session.session_lifetime_hours
)
