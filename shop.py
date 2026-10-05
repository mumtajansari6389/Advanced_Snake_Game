import pygame

SKIN_CATALOG = [
    {
        "id": "green", "name": "Classic Green", "rarity": "COMMON", "price": 0,
        "head": (0, 255, 120), "body": (0, 200, 100),
        "desc": "The original classic snake",
        "effect": "none", "requirement": None
    },
    {
        "id": "blue", "name": "Electric Blue", "rarity": "COMMON", "price": 300,
        "head": (50, 150, 255), "body": (30, 100, 200),
        "desc": "Zaps with electric energy",
        "effect": "electric", "requirement": None
    },
    {
        "id": "red", "name": "Fire Red", "rarity": "COMMON", "price": 400,
        "head": (255, 60, 60), "body": (200, 40, 40),
        "desc": "Hot enough to burn obstacles",
        "effect": "fire", "requirement": None
    },
    {
        "id": "toxic", "name": "Toxic Green", "rarity": "RARE", "price": 600,
        "head": (150, 255, 50), "body": (100, 200, 30),
        "desc": "A venomous radioactive glow",
        "effect": "toxic", "requirement": {"type": "level", "value": 3, "text": "Reach Level 3"}
    },
    {
        "id": "neon", "name": "Neon Pink", "rarity": "RARE", "price": 800,
        "head": (255, 50, 255), "body": (200, 30, 200),
        "desc": "Bright neon serpent skin",
        "effect": "glow", "requirement": None
    },
    {
        "id": "ice", "name": "Ice", "rarity": "RARE", "price": 900,
        "head": (200, 240, 255), "body": (150, 200, 255),
        "desc": "Cold as a glacier",
        "effect": "ice", "requirement": None
    },
    {
        "id": "cyber", "name": "Cyber Blue", "rarity": "RARE", "price": 1000,
        "head": (0, 255, 255), "body": (0, 150, 200),
        "desc": "Future tech design",
        "effect": "cyber", "requirement": {"type": "score", "value": 500, "text": "Score 500 in one run"}
    },
    {
        "id": "gold", "name": "Golden", "rarity": "EPIC", "price": 1500,
        "head": (255, 215, 0), "body": (200, 150, 0),
        "desc": "Solid gold, pure luxury",
        "effect": "sparkle", "requirement": None
    },
    {
        "id": "lava", "name": "Lava", "rarity": "EPIC", "price": 1800,
        "head": (255, 100, 0), "body": (200, 50, 0),
        "desc": "Magma dripping from scales",
        "effect": "fire", "requirement": {"type": "level", "value": 6, "text": "Reach Level 6"}
    },
    {
        "id": "galaxy", "name": "Purple Galaxy", "rarity": "EPIC", "price": 2000,
        "head": (150, 50, 255), "body": (80, 20, 150),
        "desc": "Contains the cosmos",
        "effect": "galaxy", "requirement": None
    },
    {
        "id": "plasma", "name": "Plasma", "rarity": "EPIC", "price": 2200,
        "head": (50, 255, 150), "body": (20, 150, 80),
        "desc": "Superheated green plasma",
        "effect": "glow", "requirement": None
    },
    {
        "id": "rainbow", "name": "Rainbow", "rarity": "LEGENDARY", "price": 3000,
        "head": (255, 255, 255), "body": (200, 200, 200),
        "desc": "Animated color shifting skin",
        "effect": "rainbow", "requirement": None
    },
    {
        "id": "shadow", "name": "Shadow", "rarity": "LEGENDARY", "price": 3500,
        "head": (40, 40, 40), "body": (20, 20, 20),
        "desc": "Darker than the void",
        "effect": "shadow", "requirement": {"type": "level", "value": 10, "text": "Reach Level 10"}
    },
    {
        "id": "cosmic", "name": "Cosmic", "rarity": "LEGENDARY", "price": 4000,
        "head": (255, 150, 200), "body": (150, 50, 100),
        "desc": "A legendary cosmic serpent",
        "effect": "galaxy", "requirement": None
    },
    {
        "id": "diamond", "name": "Diamond", "rarity": "LEGENDARY", "price": 5000,
        "head": (200, 255, 255), "body": (100, 200, 255),
        "desc": "Indestructible crystalline body",
        "effect": "sparkle", "requirement": {"type": "score", "value": 1500, "text": "Score 1500 in one run"}
    },
    {
        "id": "legendary_gold", "name": "Legendary Gold", "rarity": "LEGENDARY", "price": 10000,
        "head": (255, 255, 100), "body": (255, 200, 50),
        "desc": "The ultimate golden artifact",
        "effect": "gold_sparkle", "requirement": None
    }
]

RARITY_COLORS = {
    "COMMON": (200, 200, 200),
    "RARE": (50, 150, 255),
    "EPIC": (200, 50, 255),
    "LEGENDARY": (255, 215, 0)
}

class ShopManager:
    def __init__(self, save_manager, audio_manager):
        self.save = save_manager
        self.audio = audio_manager
        
        # Ensure default keys
        if "owned_skins" not in self.save.data:
            self.save.data["owned_skins"] = ["green"]
        if "equipped_skin" not in self.save.data:
            self.save.data["equipped_skin"] = "green"
            
    def get_all_skins(self):
        return SKIN_CATALOG
        
    def get_skin(self, index):
        return SKIN_CATALOG[index]
        
    def get_equipped_skin(self):
        eq_id = self.save.data.get("equipped_skin", "green")
        for s in SKIN_CATALOG:
            if s["id"] == eq_id:
                return s
        return SKIN_CATALOG[0]
        
    def is_owned(self, skin_id):
        return skin_id in self.save.data.get("owned_skins", [])
        
    def is_equipped(self, skin_id):
        return skin_id == self.save.data.get("equipped_skin", "green")
        
    def get_coins(self):
        return self.save.data.get("coins", 0)
        
    def is_locked(self, skin_id, current_high_score=0):
        skin = next((s for s in SKIN_CATALOG if s["id"] == skin_id), None)
        if not skin or not skin.get("requirement"):
            return False, ""
            
        req = skin["requirement"]
        if req["type"] == "level":
            unlocked = self.save.data.get("unlocked_levels", 1)
            if unlocked < req["value"]:
                return True, req["text"]
        elif req["type"] == "score":
            best = 0
            for v in self.save.data.get("high_scores", {}).values():
                if v > best: best = v
            if max(best, current_high_score) < req["value"]:
                return True, req["text"]
                
        return False, ""
        
    def buy_skin(self, skin_index, current_high_score=0):
        skin = self.get_skin(skin_index)
        
        locked, _ = self.is_locked(skin["id"], current_high_score)
        if locked:
            self.audio.play_sound("gameover")
            return False, "LOCKED"
            
        if self.is_owned(skin["id"]):
            # Equip it
            self.save.data["equipped_skin"] = skin["id"]
            self.save.save()
            self.audio.play_sound("eat")
            return True, "EQUIPPED"
            
        coins = self.get_coins()
        if coins >= skin["price"]:
            self.save.data["coins"] -= skin["price"]
            self.save.data["owned_skins"].append(skin["id"])
            self.save.data["equipped_skin"] = skin["id"]
            self.save.save()
            self.audio.play_sound("coin")
            return True, "BOUGHT"
        else:
            self.audio.play_sound("gameover")
            return False, f"Need {skin['price'] - coins} more coins"

