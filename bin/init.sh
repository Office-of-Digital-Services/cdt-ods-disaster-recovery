#!/usr/bin/env bash
set -eux

# run database migrations

python manage.py migrate
python manage.py migrate --database tasks

# collect static files

python manage.py collectstatic --no-input
