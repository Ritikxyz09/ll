#!/bin/bash
echo "Setting up virtual environment..."
python3 -m venv mybotenv
source mybotenv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting bot..."
python otp_bot.py
