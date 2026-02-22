#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Syncing dependencies with UV..."
uv sync

echo "Fetching debug package..."
uv run src/schenkers_api.py