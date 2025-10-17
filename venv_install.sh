#!/bin/bash

echo "Creating ./venv directory for virtual environment..."

python -m venv .venv
source .venv/bin/activate


pip install --upgrade numpy
pip install --upgrade --force-reinstall --no-binary=:all: simplejpeg


echo "Installing required packages from requirements.txt..."

pip install --upgrade pip
pip install -r requirements.txt