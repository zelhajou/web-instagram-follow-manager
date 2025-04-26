# Instagram Cancellation Tool

This tool automates the process of canceling pending Instagram follow requests in bulk. It provides a browser-based approach using Selenium.

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

### Docker Installation (Recommended)

```bash
# Build the Docker container
make build

# Or using docker-compose directly
docker-compose build
```

## Getting Your Pending Follow Requests from Instagram

Before running the tool, you need to obtain the HTML file containing your pending follow requests from Instagram. Follow these steps:

1. **Log in to Instagram** in your web browser
2. **Navigate to your profile** by clicking on your profile picture in the top right
3. **Click on the hamburger menu** (three horizontal lines) in the top right corner
4. **Select "Settings and privacy"**
5. **Go to "Accounts Center"**
6. **Navigate to "Your information and permissions"**
7. **Select "Download your information"**
8. **Choose "Request a download"**
9. **Select format as "HTML"** (important!)
10. **Select "Followers and following"** at minimum (you can select more if desired)
11. **Click "Submit request"**
12. **Wait for the email notification** from Instagram (may take several hours or days)
13. **Download your data** from the link provided in the email
14. **Extract the downloaded ZIP file**
15. **Locate the "pending_follow_requests.html"** file in the extracted files (usually in a "followers_and_following" folder)
16. **Copy this file** to the `./data` directory of this project

## Usage

### Preparing Your Data

```bash
# Create the data directory if it doesn't exist
make prepare-data

# Copy your pending_follow_requests.html file to the ./data directory
# On Linux/Mac:
cp /path/to/downloaded/pending_follow_requests.html ./data/

# On Windows (Command Prompt):
copy C:\path\to\downloaded\pending_follow_requests.html .\data\
```

### Running the Tool

```bash
# Using the Makefile
make run

# Or with specific HTML file
make run-with-html HTML_FILE=pending_follow_requests.html

# Or with your credentials
make run-auth USERNAME=your_username PASSWORD=your_password
```

### With Docker

```bash
# Basic run
docker-compose run --rm instagram-cancellation

# With command-line options
docker-compose run --rm instagram-cancellation --username "your_username" --password "your_password" --batch-size 10
```

### Continuing After Interruption

If the process is interrupted, you can resume from where it left off:

```bash
make continue
```

## Two-Factor Authentication Support

The tool supports 2FA:
- When 2FA is detected, the browser window will become visible
- You'll be prompted to enter your 2FA code
- Screenshots will be saved to the `./data` directory to help troubleshoot any issues

## Advanced Configuration

You can customize the tool's behavior:

```bash
# Change batch size and delays
make run-auth USERNAME=your_username PASSWORD=your_password BATCH_SIZE=15 DELAY_MIN=3 DELAY_MAX=6
```

## Troubleshooting

- **HTML File Not Found**: Make sure your `pending_follow_requests.html` file is in the `./data` directory
- **2FA Issues**: Make sure your authentication app is properly synced and check screenshots in the data directory
- **Rate Limiting**: If you encounter rate limits, increase the delay between requests
- **Failed Cancellations**: Check the `failed_cancellations.txt` file in the data directory and retry those usernames

## Files

- `instagram_cancellation.py`: Browser automation solution
- `Dockerfile`: Docker container configuration
- `docker-compose.yml`: Container orchestration
- `Makefile`: Automation commands

## Examples

### Basic Usage

```bash
# Build and run interactively
make build
make run
```

### With Pre-filled Credentials

```bash
make run-auth USERNAME=my_instagram_account PASSWORD=my_secure_password
```

### Resuming Interrupted Session

```bash
make continue
```

### Cleaning Up and Starting Fresh

```bash
make clean
make run
```