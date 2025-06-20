#!/bin/bash

# Install dependencies
pip install -r requirements/production.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Create staticfiles_build directory
mkdir -p staticfiles_build
cp -r staticfiles/* staticfiles_build/
