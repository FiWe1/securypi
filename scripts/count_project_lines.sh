#!/bin/bash

# To find out number of lines of code
# of a python project,
# run in project directory.

# to exclude directory:
# ! -path "*/dirname/*"

find securypi_app -type f \
  ! -path "*/captures/*/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/__init__.py" \
  ! -path "*/.venv/*" \
  ! -path "*/.git/*" \
  ! -path "*/instance/*" \
  ! -path "*/tests/*" \
  -exec wc -l {} + | sort -n

# to include a .file type:
# add to OR logic: \( ... -o ... -o -name "*.file" \)

# \( -name "*.py" -o -name "*.html" -o -name "*.css" \) \