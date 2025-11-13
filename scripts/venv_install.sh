#!/bin/bash

echo "Creating ./venv directory for virtual environment..."

PYTHON=python3

# ensure system packages (libcamera, picamera) are included
$PYTHON -m venv .venv --system-site-packages # @TODO Test on a fresh install without system-site, explicit numpy and simplejpeg)
. .venv/bin/activate

echo "Installing required packages from requirements.txt..."

# Ensure numpy and simplejpeg have compatible builds
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade numpy
python -m pip install --upgrade --force-reinstall simplejpeg # @TODO Test on a fresh install without reinstall)

# Install base app requirements
python -m pip install -r requirements.txt

# Install base app requirements
python -m pip install -r requirements_sensors.txt
