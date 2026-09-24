# Custom Calendar Engine (CCE)

The **Custom Calendar Engine** is a comprehensive, standalone desktop application built for worldbuilders, fantasy/sci-fi authors, and RPG gamemasters. It allows you to design completely arbitrary calendar and time systems from scratch and track story events on an absolute timeline.

## 🌟 Key Features

* **Absolute Freedom from Earth Time:** There are no hardcoded 24-hour days or 60-minute hours. You define your time hierarchy (e.g., *Wachen*, *Glockenschläge*, *Ticks*) from the top down to the smallest physical unit.
* **Flexible Calendar Creation:** Create custom weekdays, months of varying lengths (with custom colors), and Epochs/Eras (with or without a "Year 0").
* **Complex Holidays & Leap Rules:** Define holidays that fall on specific month-days or absolute days of the year. Choose whether they interrupt the normal weekday cycle. Add highly customizable leap rules (e.g., "Add 1 day to Month X every 4 years").
* **Astronomy & Multi-Planet Sync:** Configure multiple suns (Dawn, Zenith, Dusk) and moons (custom orbital cycles). The engine will automatically calculate moon phases. You can also synchronize specific points in time accurately across multiple planets in your solar system.
* **Story Event Tracker:** Add events with custom times, locations, plotlines, and characters directly to days on the calendar.
* **Export:** Export your entire story timeline sequentially to a clean Markdown file.

## 🛠️ Installation & Setup (From Source)

The application requires Python 3.10+ and relies on `customtkinter` for its modern UI.

1. **Clone or download the repository.**
2. **Install the requirements:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python main.py
   ```

## 📦 Building a Standalone Executable / Installer

You can easily package the application into a single, standalone executable (like a `.exe` on Windows or an App bundle on Mac/Linux) that does not require the user to have Python installed.

This project is pre-configured to be packed using **PyInstaller**.

### On Windows
Run the provided build script from your terminal:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py
```
After the build completes, your standalone application will be located in the newly created `dist/` folder as `CustomCalendarEngine.exe`.

### On macOS / Linux
You can use the included bash script:
```bash
chmod +x build.sh
./build.sh
```
The executable will be generated in the `dist/` directory.

> **Note on Save Files:** The engine saves all your world configurations and story events into a single `.worldcal` (JSON formatted) project file. You can load and share these files freely.
