#!/usr/bin/env bash
set -eux

# run DjangoQ cluster worker

python manage.py qcluster
