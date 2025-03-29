#!/bin/bash

# Load environment variables
echo "Loading environment variables from .env file..."
source .env

# Generate servers_config.json
echo "Generating servers_config.json..."
python scripts/generate_servers_config.py

# Install the package in development mode
echo "Installing the package in development mode..."
pip install -e .

# Start the application
echo "Starting the application..."
python -m mcp_simple_slackbot.main 
