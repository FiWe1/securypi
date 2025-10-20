#!/bin/bash

.venv/bin/python -m flask --app flaskurypi run -h 0.0.0.0 -p 5555 --debugger
