# Web Instagram Cancellation Tool

This tool automates the process of canceling pending Instagram follow requests in bulk. It provides both a browser-based approach (using Selenium) and a faster API-based approach.

## Features

- Cancel hundreds of pending Instagram follow requests automatically
- Support for Google Authenticator and other 2FA methods
- Progress tracking with resume capability
- Browser automation and API-based solutions
- Docker support for isolated environment
- Customizable delay and batch processing to avoid rate limits

## Prerequisites

- Python 3.6+
- Docker (optional, for containerized execution)
- Instagram account with pending follow requests

## Installation

### Option 1: Direct Python Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install selenium beautifulsoup4 webdriver-manager instagrapi Pillow requests
```

### Option 2: Docker Installation

```bash
# Build the Docker container
make build

# Or using docker-compose directly
docker-compose build
```

## Usage

### API-Based Method (Recommended)

The API method is significantly faster and more reliable:

```bash
python web_instagram_api_cancellation.py --html pending_follow_requests.html
```

Options:
- `--username USERNAME`: Instagram username
- `--password PASSWORD`: Instagram password
- `--html HTML_FILE`: Path to the HTML file with pending requests
- `--delay DELAY`: Delay between requests in seconds (default: 1.0)
- `--batch-size BATCH_SIZE`: Requests to process before taking a break (default: 50)
- `--continue`: Continue from last saved position
- `--usernames-file FILE`: Path to a text file with usernames (one per line)

### Browser Automation Method

For cases where the API method doesn't work:

```bash
# Using the Makefile
make run

# Or directly
python instagram_cancellation.py
```

### With Docker

```bash
make run
# or
docker-compose run --rm instagram-cancellation
```

## Two-Factor Authentication Support

Both methods support 2FA:
- The API method will prompt for your 2FA code during login
- The browser method will show the browser window for 2FA input

## Files

- `web_instagram_api_cancellation.py`: Fast API-based solution
- `instagram_cancellation.py`: Browser automation solution
- `Dockerfile`: Docker container configuration
- `docker-compose.yml`: Container orchestration
- `Makefile`: Automation commands

## Troubleshooting

- **2FA Issues**: Make sure your Google Authenticator app is properly synced
- **Rate Limiting**: If you encounter rate limits, increase the delay between requests
- **Failed Cancellations**: Check the `failed_cancellations.txt` file and retry those usernames

## Legal Notice

This tool uses unofficial API access for certain functions. Use responsibly and be aware of Instagram's terms of service regarding automation.