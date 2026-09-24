import json
import os

CONFIG_FILE = "cce_config.json"

class AppConfig:
    def __init__(self):
        self.last_opened_file = None
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_opened_file = data.get("last_opened_file")
            except Exception:
                pass

    def save(self):
        data = {
            "last_opened_file": self.last_opened_file
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

config = AppConfig()
