#!/usr/bin/env bash
set -e

HOST=db
PORT=3306
TIMEOUT=5

service redis-server start

mkdir -p /app/instance/club_folder/logs
mkdir -p /app/instance/club_folder/waiting_zone
mkdir -p /app/instance/club_folder/apk

cd /app/instance/keys
if [ ! -f "./jwtRS256-public.pem" ]; then
    openssl genrsa -out jwtRS256-private.pem 2048 && openssl rsa -in jwtRS256-private.pem -pubout -out jwtRS256-public.pem
fi
cd /app

# Let the DB start
until /wait-for-it/wait-for-it.sh --host=${HOST} --port=${PORT} --timeout=${TIMEOUT} --quiet; do
    >&2 echo "Connection not available on ${HOST}:${PORT} - waiting ${TIMEOUT} seconds"
done
