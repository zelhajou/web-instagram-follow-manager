# Web Instagram Cancellation Tool

This tool automates the process of canceling pending Instagram follow requests in bulk. It provides a browser-based approach (using Selenium).

## Features

- Cancel hundreds of pending Instagram follow requests automatically
- Support for Google Authenticator and other 2FA methods
- Progress tracking with resume capability
- Browser automation
- Docker support for isolated environment
- Customizable delay and batch processing to avoid rate limits

## Prerequisites

- Python 3.6+
- Docker (optional, for containerized execution)
- Instagram account with pending follow requests

## Installation



### Docker Installation

```bash
# Build the Docker container
make build

# Or using docker-compose directly
docker-compose build
```

## Usage

### Browser Automation Method

```bash
# Using the Makefile
make run
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

- `instagram_cancellation.py`: Browser automation solution
- `Dockerfile`: Docker container configuration
- `docker-compose.yml`: Container orchestration
- `Makefile`: Automation commands

## Troubleshooting

- **2FA Issues**: Make sure your Google Authenticator app is properly synced
- **Rate Limiting**: If you encounter rate limits, increase the delay between requests
- **Failed Cancellations**: Check the `failed_cancellations.txt` file and retry those usernames
