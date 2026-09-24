import os
import sys

# Add the project root to sys.path so 'cce' package can be found
# Also handle PyInstaller's _MEIPASS for absolute paths if needed in future
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    base_path = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, base_path)

from cce.gui.app import run

if __name__ == "__main__":
    run()
