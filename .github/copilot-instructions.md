# GitHub Copilot Instructions

## Project Overview

This project implements a Telegram bot and userbot for story-related functionality, using modern Python async practices, aiogram, and PyrogramMod. It features database integration (Supabase/PostgreSQL), profile monitoring, and anonymous story viewing.

This is a Python-based Telegram bot project called `telestories_bot` that handles story-related functionality. The project uses modern Python practices with UV for dependency management and includes both a regular bot and userbot components.

## Project Structure

```text
telestories_bot/
├── main.py                 # Main application entry point
├── bot/                    # Main bot application
├── userbot/                # Userbot application
├── config/                 # Configuration
├── db/                     # Database-related modules
├── alembic/                # Database migrations
├── scripts/                # Various scripts
├── tests/                  # Tests
├── locales/                # Localization files
├── utils/                  # Utility functions
├── pyproject.toml          # Project configuration and dependencies
└── requirements.txt        # Pinned dependencies for production
```

## Technology Stack

- **Language**: Python 3.13
- **Package Manager**: UV (modern Python package manager)
- **Bot Framework**: aiogram, PyrogramMod
- **Database**: Supabase (PostgreSQL-based)
- **Migration Tool**: Alembic
- **Project Management**: pyproject.toml (PEP 518 compliant)

## Setup

1. **Install Python 3.13** and [uv](https://astral.sh/uv/):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository** and create a virtual environment:

   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   uv pip install -e .
   ```

4. **Configure environment:**
   - Copy `.env.example` to `.env` and fill in:
     - `BOT_TOKEN`, `USERBOT_API_ID`, `USERBOT_API_HASH`, `USERBOT_PHONE_NUMBER`, `DATABASE_URL`
5. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

## Running the Bot

```bash
python main.py
```

## Development

- Run tests: `pytest`

## Coding Guidelines

- Always use lazy % formatting in logging functions (e.g., logger.info("User id=%s", user_id)), and avoid f-strings in logger functions to defer string interpolation until needed.
