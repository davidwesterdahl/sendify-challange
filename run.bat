@echo off
cd /d "%~dp0"
uv sync
uv run playwright install chromium
uv run src/schenker_client.py
pause