#!/usr/bin/env bash
set -e
HOST=db
PORT=3306
TIMEOUT=5

service redis-server start

# Let the DB start
until /wait-for-it/wait-for-it.sh --host=${HOST} --port=${PORT} --timeout=${TIMEOUT} --quiet; do
    >&2 echo "Connection not available on ${HOST}:${PORT} - waiting ${TIMEOUT} seconds"
done

# Run migrations
flask db upgrade
