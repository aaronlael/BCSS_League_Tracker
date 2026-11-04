#!/bin/bash

set -eu

echo "Starting scraper..."
python3.10 /home/aaronlael/mysite/cron_scrap_job.py
echo "Scraper finished."
