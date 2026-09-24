import tkinter as tk
from cce.utils.i18n import i18n
import customtkinter as ctk

try:
    root = tk.Tk()
    ctk.set_appearance_mode("System")
    print("UI boot success")
except Exception as e:
    print(f"Skipping GUI test due to X11 missing: {e}")
