import os
import json

BASE_DIR = os.path.dirname(__file__)
SAVE_FILE = os.path.join(BASE_DIR, "save.json")

class SaveManager:
    def __init__(self):
        self.data = {
            "coins": 0,
            "xp": 0,
            "player_level": 1,
            "high_scores": {},  # mapping level_num (str) to high score
            "unlocked_levels": 1,
            "owned_skins": ["green"],
            "equipped_skin": "green",
            "achievements": [],
            "stats": {
                "total_games": 0,
                "food_eaten": 0,
                "coins_collected": 0,
                "deaths": 0,
                "play_time_seconds": 0
            }
        }
        self.load()

    def load(self):
        # Fallback for old highscore.txt
        old_hs = 0
        hs_path = os.path.join(BASE_DIR, "highscore.txt")
        if os.path.exists(hs_path):
            try:
                with open(hs_path, "r") as f:
                    old_hs = int(f.read().strip())
            except: pass
            
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as file:
                    loaded = json.load(file)
                    # Update defaults with loaded data recursively
                    self._update_dict(self.data, loaded)
            except Exception as e:
                print(f"Error loading save: {e}")
        
        # Migrate old highscore if needed
        if old_hs > 0 and self.data["high_scores"].get("1", 0) < old_hs:
            self.data["high_scores"]["1"] = old_hs

    def _update_dict(self, target, source):
        for k, v in source.items():
            if isinstance(v, dict) and k in target and isinstance(target[k], dict):
                self._update_dict(target[k], v)
            else:
                target[k] = v

    def save(self):
        try:
            with open(SAVE_FILE, "w") as file:
                json.dump(self.data, file, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")
            
    def get_high_score(self, level_num=None):
        if level_num is None:
            # Return max of all levels if no specific level
            return max(self.data["high_scores"].values()) if self.data["high_scores"] else 0
        return self.data["high_scores"].get(str(level_num), 0)
        
    def save_high_score(self, level_num, score):
        current = self.get_high_score(level_num)
        if score > current:
            self.data["high_scores"][str(level_num)] = score
            self.save()
            return True
        return False

