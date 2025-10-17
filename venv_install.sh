#!/bin/bash

echo "Creating ./venv directory for virtual environment..."

python -m venv .venv
. .venv/bin/activate

echo "Installing required packages from requirements.txt..."

# Ensure numpy and simplejpeg have compatible builds
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install --upgrade numpy
.venv/bin/python -m pip install --upgrade --force-reinstall --no-binary=:all: simplejpeg

# Install the rest of the requirements
.venv/bin/python -m pip install -r requirements.txt