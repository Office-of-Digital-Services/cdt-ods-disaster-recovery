#!/usr/bin/env bash
set -eu

# run normal pytests
coverage run -m pytest

# clean out old coverage results
rm -rf app/static/coverage

coverage html --directory app/static/coverage
