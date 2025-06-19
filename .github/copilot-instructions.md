# GitHub Copilot Instructions

## Project Overview

This project implements a Telegram bot and userbot for story-related functionality, using modern Python async practices, aiogram, and PyrogramMod. It features database integration (Supabase/PostgreSQL), profile monitoring, and anonymous story viewing.

This is a Python-based Telegram bot project called `stories-xbot` that handles story-related functionality. The project uses modern Python practices with UV for dependency management and includes both a regular bot and userbot components.

## Project Structure

```
py-storiesxbot/
├── main.py                 # Main application entry point
├── src/                    # Source code directory
│   ├── main.py            # Alternative entry point
│   ├── bot/               # Bot implementation
│   │   └── bot.py         # Main bot logic
│   ├── userbot/           # Userbot implementation
│   │   └── userbot.py     # Userbot logic
│   ├── config/            # Configuration files
│   │   ├── settings.py    # Application settings
│   │   └── supabase.py    # Supabase database configuration
│   ├── db/                # Database layer
│   │   ├── models.py      # Database models
│   │   └── repository.py  # Data access layer
│   ├── controllers/       # Request handlers
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
└── tests/                 # Test files
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
