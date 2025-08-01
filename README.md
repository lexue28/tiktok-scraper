# TikTok API Client

A Python client for interacting with TikTok's web private APIs.

## Requirements

- Python 3.13+
- Poetry (Python package manager)

## Usage

Run the collector:
```bash
poetry run python tiktok/main.py
```

Required parameters:
- `ms_token`: Your TikTok session token (found in browser cookies after logging in)
- `batch_size`: Number of trending videos to fetch per cycle (default: 1)
- `interval`: Seconds between fetches (default: 5) 
- `cycles`: Number of collection cycles (default: infinite)

Stop collection with Ctrl+C

## Installation

### 1. Install Python 3.13
Download and install Python 3.13 from [python.org](https://www.python.org/downloads/)

### 2. Install Poetry
Poetry is required for dependency management. Install it by following the [official installation guide](https://python-poetry.org/docs/#installation).

**On Unix systems (Linux/macOS):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**On Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 3. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/filippomanzardo/tiktok-scraper.git
cd tiktok-scraper

# Install dependencies
poetry install
```

## Development Setup

This project uses several development tools:

- **MyPy** for static type checking
- **Ruff** for linting and code formatting

To install development dependencies:

```bash
poetry install --with dev
```

## Project Structure

```
tiktok-scraper/
│
├── tiktok/          # Main package directory
├── tests/           # Test directory
├── scripts/         # Scripts and utilities
│
├── pyproject.toml   # Project configuration and dependencies
└── README.md        # This file
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Running download.py
```bash
--cookies scripts\cookies.txt
```

### Type Checking & Linters
```bash
poetry run poe lint
```

## Disclaimer

This project is not affiliated with TikTok. Make sure to comply with TikTok's terms of service and API usage guidelines when using this client.
#   t i k t o k - s c r a p e r  
 