@echo off
echo Installing PyInstaller...
py -m pip install pyinstaller

echo Building Custom Calendar Engine...
py -m PyInstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py

echo Build complete! You can find the executable in the 'dist' folder.
pause
