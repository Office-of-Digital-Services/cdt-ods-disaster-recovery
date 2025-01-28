#!/usr/bin/env bash
set -eu

# initialize Django

bin/reset_db.sh

# start the web server

nginx

# start the application server

python -m gunicorn -c $GUNICORN_CONF web.wsgi
