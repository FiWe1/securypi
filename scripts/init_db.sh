#!/bin/bash

# initalise the database with the default user

.venv/bin/python -m flask --app securypi_app init-db

# returns username, password