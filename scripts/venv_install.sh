#!/bin/bash


# Install script for creating virtual environment (.venv/)
# and installing required packages, independently from platform.


PYTHON=python3

IS_RPI=false
if [ -f /proc/device-tree/model ] && grep -qi "raspberry pi" /proc/device-tree/model; then
    IS_RPI=true
    echo "Detected Raspberry Pi."

    # --system-site-packages -> ensure system packages (libcamera, picamera) are included
    echo "Creating .venv/ directory with --system-site-packages for virtual environment..."
    $PYTHON -m venv .venv --system-site-packages
else
    echo "Not on Raspberry Pi."

    # keeping package isolation on other systems
    echo "Not installing sensor libraries - creating isolated .venv/ directory..."
    $PYTHON -m venv .venv
fi

. .venv/bin/activate



echo "---"
echo "Installing required packages from requirements.txt..."
echo "---"

# Package install tools (installer + build backends)
python -m pip install --upgrade pip setuptools wheel

# Install base app requirements
python -m pip install -r requirements.txt



if $IS_RPI; then
echo "---"
echo "Installing packages for Raspberry Pi from rpi_requirements.txt..."
echo "---"
python -m pip install -r rpi_requirements.txt
# explicitly reinstalling for numpy compatibility
python -m pip install --upgrade --force-reinstall simplejpeg
fi



echo "---"
echo "Install script finished."
echo "---"
