#!/bin/bash

# runs the app on localhost:5555 in .venv (virtual pip environment)

.venv/bin/python -m flask --app securypi_app run -h localhost -p 5555

# UNSAFE! To expose the app to all networks:
# change "-h [address]" to 0.0.0.0

# you should use VPN ip instead for encryption (e.g. Tailscale)
