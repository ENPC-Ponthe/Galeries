#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
# export FLASK_APP=ponthe
flask db upgrade
