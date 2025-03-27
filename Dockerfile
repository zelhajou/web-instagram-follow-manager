FROM python:3.9-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libglib2.0-0 \
    libfontconfig1 \
    libxcb1 \
    libxkbcommon0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# Create app directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY instagram_cancellation.py .

# Create a volume for data
VOLUME /app/data

# Add these lines to your existing Dockerfile
# (near the end, before the ENTRYPOINT)

# Install xvfb for headless display
RUN apt-get update && apt-get install -y xvfb

# Create a wrapper script
RUN echo '#!/bin/bash\nxvfb-run -a -s "-screen 0 1920x1080x24" python instagram_cancellation.py "$@"' > /app/run_with_xvfb.sh
RUN chmod +x /app/run_with_xvfb.sh

# Change the entrypoint to use the wrapper script
ENTRYPOINT ["/app/run_with_xvfb.sh"]
