#!/bin/bash

# Activate the virtual environment
source /home/toshiba-inu/github/gui_white_rabbit/venv/bin/activate

# Change directory to where your Python script is located
cd /home/toshiba-inu/github/gui_white_rabbit

# Run the Python script
/usr/bin/python3 bot.py > /dev/null 2>&1 &
