from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import click


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Needs to be imported and initialised as first in the app factory.
