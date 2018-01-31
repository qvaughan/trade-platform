#!/bin/sh

until [ -f /flyway/status/completed ]; do
    echo "Flyway not completed, waiting..."
    sleep 1
done

gunicorn -b 0.0.0.0:8000 web:app
