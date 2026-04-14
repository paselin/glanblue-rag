#!/bin/bash
# Helper script to run setup_data.py from project root

cd "$(dirname "$0")/.." || exit
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python scripts/setup_data.py "$@"
