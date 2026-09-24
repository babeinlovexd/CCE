#!/bin/bash
pip install pyinstaller
pyinstaller --noconsole --onefile --windowed --add-data "assets:assets" --name="Chronix" main.py
