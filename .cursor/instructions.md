# telestories_bot Project Instructions

## Project Overview

This project implements a Telegram bot and userbot for story-related functionality, using modern Python async practices, aiogram, and PyrogramMod. It features database integration (Supabase/PostgreSQL), profile monitoring, and anonymous story viewing.

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
- **Bot Frameworks**: aiogram (bot), PyrogramMod (userbot)
- **Database**: Supabase (PostgreSQL), SQLAlchemy ORM
- **Migrations**: Alembic
- **Config**: pydantic, dotenv
- **Logging**: loguru, stdlib logging
- **Testing**: pytest
- **Package Manager**: uv

## Setup

1. **Install Python 3.13** and [uv](https://astral.sh/uv/install.sh):

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

- This will start both the bot and userbot concurrently using asyncio.

## Development

- **Run tests:**

  ```bash
  pytest
  ```

- **Format code:**

  ```bash
  ruff format .
  ```

- **Lint code:**

  ```bash
  ruff check .
  ```

- **Database migrations:**
  - Create new migration: `alembic revision --autogenerate -m "message"`
  - Apply migrations: `alembic upgrade head`

## Usage

- Send a message to the bot with a Telegram username, phone number, or direct story link.
- Monitor profiles for new stories (checked every 6 hours):
  - Add: `/monitor <@username|+19875551234>`
  - Remove: `/unmonitor <@username>`
  - List: `/monitor` or `/unmonitor` without arguments

## Coding Guidelines

- Follow PEP 8 and use type hints everywhere.
- Use async/await for all I/O operations.
- Separate concerns: handlers, services, repository, config.
- Use structured logging (loguru, stdlib).
- Always use lazy % formatting in logging functions (e.g., logger.info("User id=%s", user_id)), and avoid f-strings in logger functions to defer string interpolation until needed.
- Store secrets in environment variables, never commit credentials.
- Validate and sanitize all user input.
- Use proper error handling and logging.
- Write tests for new features and bugfixes.
- Prefer f-strings for string formatting.
- Use dependency injection for testability.

## Security & Best Practices

- Never commit API tokens or sensitive credentials.
- Use `.env` for local secrets, document required variables in README.
- Use proper authentication and authorization for sensitive actions.
- Implement rate limiting for bot commands.
- Monitor and optimize database queries.

---
For more details, see `README.md` and `.github/copilot-instructions.md`.
