# Stories XBot (Python)

A Telegram bot and userbot implementation using PyrogramMod and aiogram.

## 📊 Bot usage statistics (as of January 28, 2025)

| Metric                | Value |
|-----------------------|-------|
| **🟢 Active users count** | **12,335** |
| **👤 Total users count**  | **33,425** |
| **🔄 Requests per day**   | **~4,530** |

## Features

- Telegram Bot functionality using aiogram
- Userbot functionality using PyrogramMod
- Database integration with SQLAlchemy
- Modern async/await architecture
- Comprehensive testing suite
- Anonymous story viewing
- Profile monitoring with automatic checks every 6 hours

## Requirements

- Python 3.13
- PostgreSQL database
- Telegram API credentials (bot token and userbot session)
- uv package manager

## Installation

1. Install uv:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository and create a virtual environment:

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   uv pip install -e .
   ```

4. Copy `.env.example` to `.env` and fill in your credentials:
   - `BOT_TOKEN` - Get from [BotFather](https://t.me/BotFather)
   - `USERBOT_API_ID` and `USERBOT_API_HASH` - Get from [my.telegram.org](https://my.telegram.org)
   - `USERBOT_PHONE_NUMBER` - Phone number for the userbot account
   - `DATABASE_URL` - Your PostgreSQL connection string
   - Optional payment configuration (BTC wallet or extended public keys)

5. Run database migrations:

   ```bash
   alembic upgrade head
   ```

## Running the Bot

```bash
python -m src.main
```

## Development

- Run tests: `pytest`
- Format code: `ruff format .`
- Lint code: `ruff check .`

## Usage

Send a message to the bot with:

- Telegram username
- Phone number
- Direct link to story

### Monitoring Profiles

Monitor profiles for new stories (checked every 6 hours):

- Add: `/monitor <@username|+19875551234>`
- Remove: `/unmonitor <@username>`
- List: `/monitor` or `/unmonitor` without arguments

## License

This project is licensed under the MIT License - see the LICENSE file for details.
