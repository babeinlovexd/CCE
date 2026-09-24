#!/bin/bash
pip install pyinstaller
pyinstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py
