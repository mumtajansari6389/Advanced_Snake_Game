import random

POWERUP_TYPES = ["SPEED", "SHIELD", "SLOW", "MAGNET"]
POWERUP_COLORS = {
    "SPEED": (255, 100, 50),
    "SHIELD": (50, 100, 255),
    "SLOW": (100, 255, 255),
    "MAGNET": (255, 200, 50)
}

class PowerupManager:
    def __init__(self):
        self.active_powerup = None # What is currently on the map
        self.active_pos = [-1, -1]
        self.spawn_timer = random.randint(500, 1000)
        self.lifetime = 0
        
        # Player buffs
        self.active_buffs = {} # key: type, value: duration left in frames
        self.has_shield = False

    def reset(self):
        self.active_powerup = None
        self.spawn_timer = random.randint(500, 1000)
        self.active_buffs = {}
        self.has_shield = False

    def update(self):
        # Update map powerup
        if self.active_powerup:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.active_powerup = None
                self.spawn_timer = random.randint(800, 1500)
        else:
            if self.spawn_timer > 0:
                self.spawn_timer -= 1
                
        # Update active buffs
        expired = []
        for buff in self.active_buffs:
            self.active_buffs[buff] -= 1
            if self.active_buffs[buff] <= 0:
                expired.append(buff)
        for b in expired:
            del self.active_buffs[b]

    def spawn(self, cols, rows, obstacles, snake, food, coin_pos):
        while True:
            pos = [random.randint(2, cols-3), random.randint(2, rows-3)]
            if pos not in snake and pos not in obstacles and pos != food and pos != coin_pos:
                self.active_pos = pos
                break
        self.active_powerup = random.choice(POWERUP_TYPES)
        self.lifetime = 600 # 10 seconds to collect

    def collect(self):
        ptype = self.active_powerup
        self.active_powerup = None
        self.spawn_timer = random.randint(800, 1500)
        if ptype == "SHIELD":
            self.has_shield = True
        else:
            self.active_buffs[ptype] = 600 # 10 seconds duration
        return ptype

