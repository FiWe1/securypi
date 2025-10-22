#!/bin/bash

# To find out number of lines of code
# of a python project,
# run in project directory.

find . -type f \
  ! -path "*/__pycache__/*" \
  ! -path "*/.venv/*" \
  ! -path "*/.git/*" \
  ! -path "*/picamera_tests/*" \ # exclude directories
  -exec wc -l {} + | sort -n