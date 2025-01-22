#!/usr/bin/env bash
set -eux

# initialize pre-commit
git config --global --add safe.directory /$USER/app
pre-commit install --install-hooks --overwrite
