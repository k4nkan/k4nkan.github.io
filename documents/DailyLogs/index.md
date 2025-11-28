# DailyLogs

## Project Overview

DailyLogs is a system designed to automate the process of keeping a daily journal. It allows you to send casual messages to a Discord bot throughout the day. These messages are stored and then processed to generate a structured daily log.

The workflow is as follows:

1.  **Input**: You send messages to a Discord bot.
2.  **Storage**: The bot saves these messages and their timestamps to Supabase.
3.  **Processing**: A daily job retrieves the day's messages.
4.  **Summarization**: OpenAI's API is used to summarize the messages into a coherent diary entry.
5.  **Output**: The summary is printed (and can be pushed to Notion).

## How to Run

### Prerequisites

- Python 3.13 or higher
- A `.env` file in the root directory with the following keys:
  - `DISCORD_TOKEN`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `OPENAI_API_KEY`
  - `NOTION_API_KEY` (Optional)
  - `NOTION_DATABASE_ID` (Optional)

### 1. Run the Discord Bot

Start the bot to begin collecting messages.

```bash
python -m app.main
```

### 2. Generate Daily Log

Run the job to generate a summary for the current day (UTC based).

```bash
python -m app.jobs.generate_daily_log
```

## Architecture

The project is structured as follows:

- **`app/bot`**: Contains the Discord bot logic and event handlers.
- **`app/services`**: Handles interactions with external services.
  - `supabase.py`: Manages data storage and retrieval.
  - `openai_api.py`: Handles text summarization using LLMs.
  - `notion.py`: Interfaces with Notion for publishing logs.
- **`app/jobs`**: Contains scripts for batch processing, such as `generate_daily_log.py`.
- **`app/configs`**: Configuration modules for loading environment variables.


---

[`Go Back to Top Page`](https://k4nkan.github.io/)
