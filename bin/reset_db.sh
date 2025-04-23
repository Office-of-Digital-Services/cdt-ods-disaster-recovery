#!/usr/bin/env bash
set -ex

# whether to reset database file, defaults to true
DB_RESET="${DJANGO_DB_RESET:-true}"

if [[ $DB_RESET = true ]]; then
    python manage.py reset_db

    # run database migrations and other initialization
    bin/init.sh

    # create a superuser account for backend admin access
    # set username, email, and password using environment variables
    # DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD
    python manage.py createsuperuser --no-input
else
    echo "DB_RESET is false, skipping"
fi

valid_fixtures=$(echo "$DJANGO_DB_FIXTURES" | grep -e fixtures\.json$ || test $? = 1)

if [[ -n "$valid_fixtures" ]]; then
    # load data fixtures
    python manage.py loaddata $DJANGO_DB_FIXTURES
else
    echo "No JSON fixtures to load"
fi
