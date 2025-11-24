# Daily Logs

A Discord bot for managing daily logs using the Discord API and Notion API.

## Features

- **Discord Bot**: Interacts with users on Discord to collect daily logs.
- **Notion Integration**: Fetches and updates daily logs in a Notion database.

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord Bot Token
- A Notion Integration Token and Database ID

### Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd DailyLogs
    ```

2.  **Install dependencies**:

    ```bash
    pip install discord.py requests python-dotenv
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory and add your keys:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    NOTION_API_KEY=your_notion_api_key
    NOTION_DATABASE_ID=your_notion_database_id
    ```

## Usage

Run the bot using the following command:

```bash
python scripts/main.py
```

To test the Notion integration separately:

```bash
python scripts/notion.py
```


---

[`Go Back to Top Page`](https://k4nkan.github.io/)
