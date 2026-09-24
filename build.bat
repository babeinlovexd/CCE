@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building Custom Calendar Engine...
pyinstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py

echo Build complete! You can find the executable in the 'dist' folder.
pause
