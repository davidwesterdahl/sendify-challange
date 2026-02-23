#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Syncing dependencies with UV..."
uv sync

echo "Installing chromium for playwright"
uv run playwright install chromium

echo "Fetching debug package..."
uv run src/schenkerc_client.py