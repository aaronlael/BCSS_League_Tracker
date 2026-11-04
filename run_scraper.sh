#!/bin/bash

set -eu

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting scraper..."
python3.10 "$SCRIPT_DIR/cron_scrap_job.py"
echo "Scraper finished."
