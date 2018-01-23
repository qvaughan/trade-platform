#!/bin/sh

until [ -f /flyway/status/completed ]; do
    echo "Flyway not completed, waiting..."
    sleep 1
done

python data_collector.py