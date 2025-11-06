#!/bin/bash

.venv/bin/python -m flask --app flaskurypi run -h localhost -p 5554 --debugger

# change "-h [address]" to 0.0.0.0 for all networks - unsafe!
# use VPN ip