# TeleGraphite: Telegram Scraper & JSON Exporter & telegram chanels scraper


A tool to fetch and save posts from public Telegram channels.
![TeleGraphite Screenshot](logo.png)

## Features

- Fetch posts from multiple Telegram channels
- Save posts as JSON files (with contact exports: emails, phone numbers, links)
- Download and save media files (photos, documents videos)
- Deduplicate posts to avoid saving the same content twice
- Run once or continuously with a specified interval
- Filter posts by keywords or content type (text-only, media-only)
- Schedule fetching at specific days and times

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/hamodywe/telegraphite.git
cd telegraphite

# Install the package
pip install -e .
```

### Using pip

```bash
pip install telegraphite
```

## Setup

1. Create a Telegram API application:
   - Go to https://my.telegram.org/
   - Log in with your phone number
   - Go to 'API development tools'
   - Create a new application
   - Note your API ID and API Hash

2. Create a `.env` file in your project directory with the following content:

```
API_ID=your_api_id
API_HASH=your_api_hash
```

3. Create a `channels.txt` file with one channel username per line:

```
@channel1
@channel2
channel3
```

## Usage

### Command Line Interface

TeleGraphite provides a command-line interface for fetching posts:

```bash
# Fetch posts once and exit
telegraphite once

# Fetch posts continuously with a 1-hour interval
telegraphite continuous --interval 3600
```

### Options

```
-c, --channels-file  Path to file containing channel usernames (default: channels.txt)
-d, --data-dir       Directory to store posts and media (default: data)
-e, --env-file       Path to .env file with API credentials (default: .env)
-l, --limit          Maximum number of posts to fetch per channel (default: 10)
-v, --verbose        Enable verbose logging
-i, --interval       Interval between fetches in seconds (default: 3600, only for continuous mode)
--config             Path to YAML configuration file

# Filter options
--keywords           Filter posts containing specific keywords
--media-only         Only fetch posts containing media (photos, documents)
--text-only          Only fetch posts containing text

# Schedule options
--days               Days of the week to run the fetcher (monday, tuesday, etc.)
--times              Times of day to run the fetcher in HH:MM format
```

### Configuration File

You can also use a YAML configuration file to specify options:

```yaml
# Directory to store posts and media
data_dir: data

# Path to file containing channel usernames
channels_file: channels.txt

# Maximum number of posts to fetch per channel
limit: 10

# Interval between fetches in seconds (for continuous mode)
interval: 3600

# Filters for posts
filters:
  # Keywords to filter posts (only fetch posts containing these keywords)
  keywords:
    - important
    - announcement
  # Only fetch posts containing media (photos, documents)
  media_only: false
  # Only fetch posts containing text
  text_only: false

# Schedule for fetching posts (for continuous mode)
schedule:
  # Days of the week to run the fetcher
  days:
    - monday
    - wednesday
    - friday
  # Times of day to run the fetcher (HH:MM format)
  times:
    - "09:00"
    - "18:00"
```

To use a configuration file:

```bash
telegraphite --config config.yaml once
```

Command-line arguments will override settings in the configuration file.

### Examples

```bash
# Fetch 20 posts from each channel and save to custom directory
telegraphite once --limit 20 --data-dir custom_data

# Use custom channels file and environment file
telegraphite once --channels-file my_channels.txt --env-file my_env.env

# Run continuously with 30-minute interval and verbose logging
telegraphite continuous --interval 1800 --verbose

# Fetch only posts containing specific keywords
telegraphite once --keywords announcement important news

# Fetch only posts containing media
telegraphite once --media-only

# Run continuously on specific days and times
telegraphite continuous --days monday wednesday friday --times 09:00 18:00

# Combine filters and scheduling
telegraphite continuous --keywords important --media-only --days monday friday --times 12:00
```

## Data Structure

Posts and media are saved in the following structure:

```
data/
  channel1/
    posts.json
    media/
      20230101_123456_123.jpg
      20230101_123456_124.pdf
  channel2/
    posts.json
    media/
      ...
```

Each `posts.json` file contains an array of post objects with the following structure:

```json
[
  {
    "channel": "channel1",
    "post_id": 123,
    "date": "2023-01-01T12:34:56Z",
    "text": "Post content",
    "images": ["media/20230101_123456_123.jpg"]
  },
  ...
]
```

## License

MIT
