#!/bin/sh

rm -f /flyway/status/completed

set -e

cmd="$@"

until $cmd; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

touch /flyway/status/completed