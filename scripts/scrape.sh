#!/bin/bash
# Scrape GameWith data with venv activation

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)"

# Activate venv
source venv/bin/activate

# Run scraper
python scripts/scrape_and_index.py "$@"
