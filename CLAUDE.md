# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube setlist analyzer for 白珠ウタノ (Shiratama Utano) - tracks "六甲おろし" (Rokko Oroshi) performances from a specific YouTube playlist. Uses YouTube Data API v3 to fetch playlist videos and analyze comments.

## Tech Stack

- **Python 3.14** with **uv** as the package manager
- **google-api-python-client** for YouTube Data API v3
- **python-dotenv** for environment variable management
- **Docker** + **docker-compose** for containerized execution

## Commands

```bash
# Install dependencies (local)
uv sync

# Run the main script (local)
uv run python check_youtube_utano.py

# Docker build and run
docker compose up --build

# Run in existing container
docker compose exec app python check_youtube_utano.py
```

## Environment

Requires a `.env` file with `YOUTUBE_API_KEY` set. The `.env` file is gitignored.

## Architecture

Single-script application (`check_youtube_utano.py`) that connects to the YouTube Data API using an API key. The target playlist is hardcoded as `PLUi5gdZovvGlyVfVOyzmgOwZ8jd0bT2mS`. The project is in early development — the script currently only validates API key connectivity.
