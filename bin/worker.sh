#!/usr/bin/env bash
set -eux

# run DjangoQ cluster worker once
# this script is intended to be run inside a scheduled job

python manage.py qcluster --run-once
