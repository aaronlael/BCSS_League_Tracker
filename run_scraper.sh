#!/bin/bash

set -eu

: "${host:?Set host in the environment}"
: "${user:?Set user in the environment}"
: "${password:?Set password in the environment}"
: "${database:?Set database in the environment}"

echo "Starting scraper for $database..."
python3.10 /home/aaronlael/mysite/cron_scrap_job.py
echo "Scraper finished."
