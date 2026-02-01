#!/bin/bash

# Startup script for Enhanced Trading Analysis System

echo "Starting Enhanced Trading Analysis System..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting the trading system..."
python app.py

# Deactivate virtual environment when done
deactivate