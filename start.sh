#!/bin/bash

# Activate the virtual environment
source /venv/bin/activate

# Run the Python script
/usr/bin/python3 bot.py > /dev/null 2>&1 &
