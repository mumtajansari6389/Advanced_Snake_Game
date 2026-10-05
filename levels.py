class LevelManager:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.levels = {
            1: {
                "name": "Level 1: The Forest",
                "bg_color": (20, 35, 25),
                "snake_head": (0, 255, 120),
                "snake_body": (0, 200, 100),
                "food_color": (255, 40, 40),
                "speed": 10,
                "objective_type": "score",
                "objective_value": 50,
                "obstacles": []
            },
            2: {
                "name": "Level 2: Night Time",
                "bg_color": (20, 25, 40),
                "snake_head": (100, 150, 255),
                "snake_body": (80, 120, 220),
                "food_color": (255, 200, 40),
                "speed": 13,
                "objective_type": "score",
                "objective_value": 100,
                "obstacles": self.generate_borders()
            },
            3: {
                "name": "Level 3: The Desert",
                "bg_color": (45, 30, 20),
                "snake_head": (255, 150, 50),
                "snake_body": (220, 120, 40),
                "food_color": (100, 255, 255),
                "speed": 16,
                "objective_type": "collect_food",
                "objective_value": 15,
                "obstacles": self.generate_cross()
            },
            4: {
                "name": "Level 4: Ice Cavern",
                "bg_color": (20, 40, 45),
                "snake_head": (50, 255, 255),
                "snake_body": (40, 220, 220),
                "food_color": (255, 100, 255),
                "speed": 19,
                "objective_type": "score",
                "objective_value": 200,
                "obstacles": self.generate_maze()
            },
            5: {
                "name": "Level 5: Neon Future",
                "bg_color": (30, 15, 40),
                "snake_head": (255, 50, 255),
                "snake_body": (220, 40, 220),
                "food_color": (50, 255, 100),
                "speed": 22,
                "objective_type": "survival",
                "objective_value": 60,
                "obstacles": self.generate_hard_maze()
            }
        }

    def generate_borders(self):
        obs = []
        for x in range(2, self.cols - 2):
            obs.append([x, 2])
            obs.append([x, self.rows - 3])
        for y in range(2, self.rows - 2):
            obs.append([2, y])
            obs.append([self.cols - 3, y])
        return obs

    def generate_cross(self):
        obs = []
        mid_x = self.cols // 2
        mid_y = self.rows // 2
        for x in range(mid_x - 6, mid_x + 6):
            obs.append([x, mid_y])
            obs.append([x, mid_y - 1])
        for y in range(mid_y - 6, mid_y + 6):
            obs.append([mid_x, y])
            obs.append([mid_x - 1, y])
        return obs

    def generate_maze(self):
        obs = []
        # Top-left and top-right blocks
        for x in range(5, 10): 
            obs.append([x, 5])
            obs.append([self.cols - x - 1, 5])
        # Bottom-left and bottom-right blocks
        for x in range(5, 10): 
            obs.append([x, self.rows - 6])
            obs.append([self.cols - x - 1, self.rows - 6])
        # Center vertical lines
        for y in range(8, self.rows - 8): 
            obs.append([self.cols // 2 - 2, y])
            obs.append([self.cols // 2 + 1, y])
        return obs
        
    def generate_hard_maze(self):
        obs = self.generate_borders()
        obs.extend(self.generate_cross())
        return obs

    def get_level(self, level_num, difficulty=1):
        if level_num <= 5:
            base_level = self.levels.get(level_num)
        else:
            # Procedural Generation for Infinite Levels
            import random
            themes = [
                {"bg_color": (20, 15, 30), "snake_head": (150, 50, 200), "snake_body": (100, 30, 150), "food_color": (255, 100, 100)},
                {"bg_color": (30, 10, 10), "snake_head": (255, 150, 50), "snake_body": (200, 100, 50), "food_color": (100, 255, 255)},
                {"bg_color": (10, 30, 20), "snake_head": (50, 255, 150), "snake_body": (30, 200, 100), "food_color": (255, 50, 255)},
                {"bg_color": (25, 25, 25), "snake_head": (255, 255, 0), "snake_body": (200, 200, 0), "food_color": (0, 255, 255)}
            ]
            base_level = dict(random.choice(themes))
            base_level["name"] = f"Endless Level {level_num}"
            
            # Procedural Objectives
            obj_type = random.choice(["score", "collect_food", "survival"])
            if obj_type == "score": base_level["objective_value"] = 150 + (level_num * 10)
            elif obj_type == "collect_food": base_level["objective_value"] = 15 + (level_num)
            elif obj_type == "survival": base_level["objective_value"] = 45 + (level_num * 2)
            
            base_level["objective_type"] = obj_type
            base_level["speed"] = min(20, 12 + (level_num // 2))
            
            # Procedural Obstacles
            base_level["obstacles"] = self.generate_borders()
            obs_type = random.choice(["cross", "pillars", "none"])
            if obs_type == "cross": 
                base_level["obstacles"].extend(self.generate_cross())
            elif obs_type == "pillars":
                for x in range(5, self.cols-5, 4):
                    for y in range(4, self.rows-4, 4):
                        if (x+y) % 3 == 0: base_level["obstacles"].append([x, y])
            
        # Create a copy so we don't modify the original level definition directly
        level = dict(base_level)
        level["obstacles"] = list(base_level["obstacles"])
        
        # Change background structure (obstacles) based on difficulty
        if difficulty == 0:  # Easy
            # Remove half of the obstacles to make it much easier
            level["obstacles"] = level["obstacles"][::2]
        elif difficulty == 2:  # Hard
            # Add extra hazard structures to the background for hard mode
            extra_obs = []
            # Add corner blocks
            extra_obs.extend([[4, 4], [self.cols - 5, 4], [4, self.rows - 5], [self.cols - 5, self.rows - 5]])
            # Add some inner dots
            mid_x, mid_y = self.cols // 2, self.rows // 2
            extra_obs.extend([[mid_x - 4, mid_y - 4], [mid_x + 4, mid_y + 4]])
            level["obstacles"] = level["obstacles"] + extra_obs
            
        return level

