# TikTok API Client

A Python client for interacting with TikTok's web private APIs.

## Requirements
- Python 3.13+
- Poetry (Python package manager)

## Installation

### 1) Install Python 3.13
Download and install Python 3.13 from the [official site](https://www.python.org/downloads/).

### 2) Install Poetry
Follow the [Poetry install guide](https://python-poetry.org/docs/#installation).

**Linux/macOS:** run `curl -sSL https://install.python-poetry.org | python3 -`  
**Windows (PowerShell):** run `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

### 3) Clone and install dependencies
Run:
- `git clone https://github.com/lexue28/tiktok-scraper.git`
- `cd tiktok-scraper`
- `poetry install`

Tip: to open a virtualenv shell use `poetry shell`.

## Usage

Run the collector (example):
- `poetry run python tiktok/main.py --ms-token "<YOUR_MS_TOKEN>" --batch-size 1 --interval 5 --cycles 10`

**Parameters**
- `--ms-token` (string): Your TikTok session token (from browser cookies after logging in).
- `--batch-size` (int): Number of trending videos to fetch per cycle (default: `1`).
- `--interval` (int): Seconds between fetches (default: `5`).
- `--cycles` (int): Number of collection cycles (omit for infinite).

Stop the collector with **Ctrl+C**.

## Download script

If you use a separate downloader (e.g., `scripts/download.py`) that needs cookies:

**macOS/Linux:** `poetry run python scripts/download.py --cookies scripts/cookies.txt`  
**Windows (PowerShell):** `poetry run python scripts\download.py --cookies scripts\cookies.txt`

Adjust flags to match your script (e.g., `--input`, `--out-dir`, etc.).

## Tests
- `poetry run pytest`

## Type checking & linting
- `poetry run poe lint`

## Project structure
- `tiktok/` — Main package  
- `tests/` — Tests  
- `scripts/` — Scripts and utilities  
- `pyproject.toml` — Project configuration and dependencies  
- `README.md`

## Disclaimer
This project is not affiliated with TikTok. Ensure your usage complies with TikTok’s Terms of Service and applicable laws.
