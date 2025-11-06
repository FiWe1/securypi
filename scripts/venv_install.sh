#!/bin/bash

echo "Creating ./venv directory for virtual environment..."

PYTHON=python3

# ensure system packages (libcamera, picamera) are included
$PYTHON -m venv .venv --system-site-packages # TODO(Test on a fresh install without system-site)
. .venv/bin/activate

echo "Installing required packages from requirements.txt..."

# Ensure numpy and simplejpeg have compatible builds
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install --upgrade numpy
.venv/bin/python -m pip install --upgrade --force-reinstall simplejpeg # TODO(Test on a fresh install without reinstall)

# Install the rest of the requirements
.venv/bin/python -m pip install -r requirements.txt
