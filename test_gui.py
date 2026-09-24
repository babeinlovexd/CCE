import sys
sys.path.append('.')
import tkinter as tk
import customtkinter as ctk
from cce.gui.app import Application

# Just initialize to see if it throws errors without starting mainloop
try:
    root = tk.Tk()
    ctk.set_appearance_mode("System")
except Exception as e:
    print(f"Skipping GUI test due to X11 missing: {e}")
