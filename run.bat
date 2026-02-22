@echo off
cd /d "%~dp0"
uv sync
uv run src/schenkers_api.py
pause