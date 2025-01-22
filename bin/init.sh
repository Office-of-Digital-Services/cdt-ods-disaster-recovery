#!/usr/bin/env bash
set -eux

# run database migrations

python manage.py migrate

# collect static files

python manage.py collectstatic --no-input
