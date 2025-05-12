#!/usr/bin/env bash
set -ex

# Ensure databases, users, migrations, and superuser are set up
python manage.py ensure_db

# Load data fixtures (if any)
valid_fixtures=$(echo "$DJANGO_DB_FIXTURES" | grep -e fixtures\.json$ || test $? = 1)

if [[ -n "$valid_fixtures" ]]; then
    python manage.py loaddata $DJANGO_DB_FIXTURES
else
    echo "No JSON fixtures to load"
fi
