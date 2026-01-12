#!/bin/bash
# Simple setup script for Linux/Mac
echo "Setting up EduPace development environment..."

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"

