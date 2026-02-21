#!/bin/bash
set -e

echo "Syncing dependencies with UV..."
uv sync

echo "Fetching debug package..."
uv run src/tester.py