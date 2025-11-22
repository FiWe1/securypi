#!/bin/bash

# initalise the database with the default user

source .venv/bin/activate
flask --app securypi_app init-db

# returns username, password