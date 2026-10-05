import os
import json

BASE_DIR = os.path.dirname(__file__)
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

WIDTH = 640
HEIGHT = 480
BLOCK = 20

ROWS = HEIGHT // BLOCK
COLS = WIDTH // BLOCK

FPS = 60

class SettingsManager:
    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.fullscreen = False
        self.difficulty = 1  # 0: Easy, 1: Medium, 2: Hard
        self.skin = 0
        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as file:
                    data = json.load(file)
                    self.sound_enabled = data.get("sound_enabled", True)
                    self.music_enabled = data.get("music_enabled", True)
                    self.fullscreen = data.get("fullscreen", False)
                    self.difficulty = data.get("difficulty", 1)
                    self.skin = data.get("skin", 0)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        data = {
            "sound_enabled": self.sound_enabled,
            "music_enabled": self.music_enabled,
            "fullscreen": self.fullscreen,
            "difficulty": self.difficulty,
            "skin": getattr(self, 'skin', 0)
        }
        try:
            with open(SETTINGS_FILE, "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

