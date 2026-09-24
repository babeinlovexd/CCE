@echo off
echo Installing PyInstaller...
py -m pip install pyinstaller

echo Building Chronix...
py -m PyInstaller --noconsole --onefile --windowed --icon="assets/icon.ico" --add-data "assets;assets" --name="Chronix" main.py

echo Build complete! You can find the executable in the 'dist' folder.
pause
