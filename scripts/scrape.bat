@echo off
REM Scrape GameWith data with venv activation (Windows)

cd /d %~dp0..
set PYTHONPATH=%CD%

REM Activate venv
call venv\Scripts\activate.bat

REM Run scraper
python scripts\scrape_and_index.py %*
