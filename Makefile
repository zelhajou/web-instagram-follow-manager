# Makefile for Instagram Cancellation Docker project

# Variables
DOCKER_COMPOSE = docker compose
DATA_DIR = ./data
USERNAME ?= 
PASSWORD ?=
BATCH_SIZE ?= 10
DELAY_MIN ?= 2
DELAY_MAX ?= 4

.PHONY: help build run run-interactive clean logs restart stop status shell continue

# Default target
help:
	@echo "Instagram Cancellation Tool - Makefile Help"
	@echo "-----------------------------------------"
	@echo "Available commands:"
	@echo "  make build            - Build the Docker container"
	@echo "  make run              - Run the tool (interactive mode)"
	@echo "  make run-auth         - Run with provided credentials (USERNAME=x PASSWORD=y)"
	@echo "  make continue         - Continue from last saved position"
	@echo "  make clean            - Remove progress files and restart"
	@echo "  make stop             - Stop the running container"
	@echo "  make restart          - Restart the container"
	@echo "  make status           - Check container status"
	@echo "  make shell            - Open a shell in the container"
	@echo "  make logs             - View container logs"
	@echo ""
	@echo "Advanced options:"
	@echo "  make run-auth USERNAME=your_username PASSWORD=your_password BATCH_SIZE=15"
	@echo "  make run-auth DELAY_MIN=3 DELAY_MAX=6"
	@echo ""
	@echo "Example usage:"
	@echo "  make build"
	@echo "  make run"
	@echo ""

# Build the Docker container
build:
	@echo "Building Docker container..."
	@mkdir -p $(DATA_DIR)
	$(DOCKER_COMPOSE) build

# Run the tool in interactive mode
run: build
	@echo "Starting the Instagram Cancellation Tool..."
	$(DOCKER_COMPOSE) run --rm instagram-cancellation

# Run with provided credentials
run-auth: build
	@if [ -z "$(USERNAME)" ] || [ -z "$(PASSWORD)" ]; then \
		echo "Error: USERNAME and PASSWORD must be provided."; \
		echo "Usage: make run-auth USERNAME=your_username PASSWORD=your_password"; \
		exit 1; \
	fi
	@echo "Running with provided credentials..."
	$(DOCKER_COMPOSE) run --rm instagram-cancellation \
		--username "$(USERNAME)" \
		--password "$(PASSWORD)" \
		--batch-size $(BATCH_SIZE) \
		--delay-min $(DELAY_MIN) \
		--delay-max $(DELAY_MAX)

# Continue from last saved position
continue: build
	@echo "Continuing from last saved position..."
	$(DOCKER_COMPOSE) run --rm instagram-cancellation --continue

# Clean up progress files to restart
clean:
	@echo "Cleaning up progress files..."
	@rm -f $(DATA_DIR)/instagram_cancellation_progress.json $(DATA_DIR)/failed_cancellations.txt
	@echo "Progress files have been removed. You can start fresh now."

# Stop the running container
stop:
	@echo "Stopping the container..."
	$(DOCKER_COMPOSE) stop

# Restart the container
restart: stop
	@echo "Restarting the container..."
	$(DOCKER_COMPOSE) up -d

# Check container status
status:
	@echo "Container status:"
	$(DOCKER_COMPOSE) ps

# Open a shell in the container
shell:
	@echo "Opening a shell in the container..."
	$(DOCKER_COMPOSE) run --rm instagram-cancellation /bin/bash

# View container logs
logs:
	@echo "Container logs:"
	$(DOCKER_COMPOSE) logs

# Prepare the data directory
prepare-data:
	@mkdir -p $(DATA_DIR)
	@echo "Data directory created: $(DATA_DIR)"
	@echo "Place your pending_follow_requests.html file in this directory."

# Run with specific HTML file
run-with-html: build
	@echo "Running with specific HTML file..."
	@if [ -z "$(HTML_FILE)" ]; then \
		echo "Error: HTML_FILE must be provided."; \
		echo "Usage: make run-with-html HTML_FILE=pending_follow_requests.html"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) run --rm instagram-cancellation --html "/app/data/$(HTML_FILE)"