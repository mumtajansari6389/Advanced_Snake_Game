import os
import random
import pygame

from settings import SettingsManager, WIDTH, HEIGHT, BLOCK, ROWS, COLS, FPS
from ui import Button, draw_text, LevelNodeButton
from levels import LevelManager
from save_manager import SaveManager
from audio_manager import AudioManager
from effects import ParticleSystem
from powerups import PowerupManager, POWERUP_COLORS
import shop

class Game:
    def __init__(self):
        pygame.init()

        self.settings = SettingsManager()
        self.save_manager = SaveManager()
        self.audio_manager = AudioManager()
        self.shop_manager = shop.ShopManager(self.save_manager, self.audio_manager)
        self.particle_system = ParticleSystem()
        self.powerup_manager = PowerupManager()
        
        self.combo_count = 0
        self.combo_timer = 0
        
        self.audio_manager.apply_settings(self.settings.sound_enabled, self.settings.music_enabled)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Professional Snake Game")

        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = "MAIN_MENU"
        self.level_manager = LevelManager(COLS, ROWS)
        self.current_level_num = 1
        self.current_level_data = None
        
        # Load Fonts
        self.title_font = pygame.font.SysFont("Arial", 48, True)
        self.btn_font = pygame.font.SysFont("Arial", 24, True)
        self.hud_font = pygame.font.SysFont("Arial", 20, True)
        self.sig_font = pygame.font.SysFont("Arial", 22, True)

        # Cinematic Menu Elements
        self.bg_particles = [
            {"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), 
             "speed": random.uniform(0.5, 2.0), "size": random.randint(2, 5), 
             "color": random.choice([(0, 255, 200), (255, 100, 200), (100, 150, 255)])} 
            for _ in range(40)
        ]

        # Setup Buttons
        btn_w, btn_h = 240, 45
        center_x = WIDTH // 2 - btn_w // 2
        
        # Main Menu Buttons - Vibrant and Kid Friendly
        self.play_btn = Button(center_x, 180, btn_w, 55, "PLAY GAME", self.btn_font, (46, 204, 113), (39, 174, 96))
        self.settings_btn = Button(center_x, 250, btn_w, 55, "SETTINGS", self.btn_font, (52, 152, 219), (41, 128, 185))
        self.shop_btn = Button(center_x, 320, btn_w, 55, "SHOP", self.btn_font, (241, 196, 15), (243, 156, 18))
        self.quit_btn = Button(center_x, 390, btn_w, 55, "QUIT", self.btn_font, (231, 76, 60), (192, 57, 43))
        
        # Shop UI Buttons
        self.shop_skin_index = 0
        self.shop_prev_btn = Button(center_x - 120, 250, 40, 40, "<", self.btn_font, (100,100,100), (150,150,150))
        self.shop_next_btn = Button(center_x + 120, 250, 40, 40, ">", self.btn_font, (100,100,100), (150,150,150))
        self.shop_action_btn = Button(center_x, 350, btn_w, 50, "BUY", self.btn_font, (40,150,80), (60,200,100))
        self.shop_back_btn = Button(center_x, HEIGHT - 70, btn_w, 45, "BACK", self.btn_font, (80,80,80), (120,120,120))
        
        # Settings Buttons (More buttons now)
        self.sound_btn = Button(center_x, 110, btn_w, btn_h, "SOUND: ON", self.btn_font, (100, 100, 100), (150, 150, 150))
        self.music_btn = Button(center_x, 170, btn_w, btn_h, "MUSIC: ON", self.btn_font, (100, 100, 100), (150, 150, 150))
        self.diff_btn = Button(center_x, 230, btn_w, btn_h, "DIFFICULTY: MED", self.btn_font, (100, 100, 100), (150, 150, 150))
        self.skin_btn = Button(center_x, 290, btn_w, btn_h, "SKIN: DYNAMIC", self.btn_font, (100, 100, 100), (150, 150, 150))
        self.back_btn = Button(center_x, 350, btn_w, btn_h, "BACK TO MENU", self.btn_font, (80, 80, 80), (120, 120, 120))
        self.update_settings_btn_text()

        # Pause & Game Over Buttons
        self.resume_btn = Button(center_x, 150, btn_w, 50, "RESUME", self.btn_font, (40, 150, 80), (60, 200, 100))
        self.retry_btn = Button(center_x, 150, btn_w, 50, "RETRY", self.btn_font, (40, 150, 80), (60, 200, 100))
        self.map_btn = Button(center_x, 220, btn_w, 50, "LEVEL MAP", self.btn_font, (200, 150, 40), (230, 180, 60))
        self.menu_btn = Button(center_x, 290, btn_w, 50, "MAIN MENU", self.btn_font, (80, 80, 150), (100, 100, 200))
        self.map_back_btn = Button(center_x, HEIGHT - 70, btn_w, 45, "BACK TO MENU", self.btn_font, (80, 80, 80), (120, 120, 120))
        self.level_nodes = []
        
        # In-Game Control Buttons (Bottom Right)
        self.hud_btn_font = pygame.font.SysFont("Arial", 16, True)
        self.pause_icon_btn = Button(WIDTH - 145, HEIGHT - 45, 40, 35, "||", self.hud_btn_font, (200, 150, 40), (230, 180, 60))
        self.full_icon_btn = Button(WIDTH - 95, HEIGHT - 45, 40, 35, "[ ]", self.hud_btn_font, (40, 150, 200), (60, 180, 230))
        self.min_icon_btn = Button(WIDTH - 45, HEIGHT - 45, 40, 35, "_", self.hud_btn_font, (200, 60, 60), (230, 80, 80))

        # Game Variables
        self.score = 0
        self.food_particles = []
        self.stars = [
            {"x": random.randint(0, WIDTH - 1), "y": random.randint(0, HEIGHT - 1), 
             "size": random.randint(1, 3), "phase": random.randint(0, 100)} for _ in range(70)
        ]
        self.apple_image = self._load_apple_image()
        
        self.transition_timer = 0
        self.food_scale = 1.0
        self.food_grow = True
        self.map_scroll_y = 0
        self.is_map_dragging = False
        self.swipe_start = None

    def toggle_fullscreen(self):
        self.settings.fullscreen = not self.settings.fullscreen
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.settings.save_settings()

    def _load_apple_image(self):
        apple_path = os.path.join(os.path.dirname(__file__), "assets", "images", "apple.png")
        if os.path.exists(apple_path):
            try:
                return pygame.image.load(apple_path).convert_alpha()
            except pygame.error:
                pass
        return None

    def update_settings_btn_text(self):
        # Update Audio Manager
        self.audio_manager.apply_settings(self.settings.sound_enabled, self.settings.music_enabled)
        
        # Sound & Music
        self.sound_btn.text = "SOUND: ON" if self.settings.sound_enabled else "SOUND: OFF"
        self.sound_btn.bg_color = (40, 150, 80) if self.settings.sound_enabled else (180, 60, 60)
        self.music_btn.text = "MUSIC: ON" if self.settings.music_enabled else "MUSIC: OFF"
        self.music_btn.bg_color = (40, 150, 80) if self.settings.music_enabled else (180, 60, 60)
        
        # Difficulty
        diff_texts = {0: "DIFF: EASY", 1: "DIFF: NORMAL", 2: "DIFF: HARD"}
        diff_colors = {0: (40, 150, 80), 1: (200, 150, 40), 2: (180, 60, 60)}
        self.diff_btn.text = diff_texts[self.settings.difficulty]
        self.diff_btn.bg_color = diff_colors[self.settings.difficulty]
        
        # Skin
        if not hasattr(self.settings, 'skin'): self.settings.skin = 0
        skin_texts = {0: "SKIN: DYNAMIC", 1: "SKIN: CLASSIC", 2: "SKIN: AQUA", 3: "SKIN: FIRE"}
        skin_colors = {0: (120, 80, 200), 1: (40, 180, 80), 2: (40, 180, 220), 3: (220, 80, 40)}
        self.skin_btn.text = skin_texts[self.settings.skin]
        self.skin_btn.bg_color = skin_colors[self.settings.skin]

    def update_shop_action_btn(self):
        skin = self.shop_manager.get_skin(self.shop_skin_index)
        
        # Get highest score to check locks
        high_score = 0
        for v in self.save_manager.data.get("high_scores", {}).values():
            if v > high_score: high_score = v
            
        is_locked, lock_text = self.shop_manager.is_locked(skin["id"], high_score)
        
        if is_locked:
            self.shop_action_btn.text = "LOCKED"
            self.shop_action_btn.bg_color = (80, 80, 80)
        elif self.shop_manager.is_equipped(skin["id"]):
            self.shop_action_btn.text = "EQUIPPED"
            self.shop_action_btn.bg_color = (100, 100, 100)
        elif self.shop_manager.is_owned(skin["id"]):
            self.shop_action_btn.text = "EQUIP"
            self.shop_action_btn.bg_color = (40, 150, 80)
        else:
            self.shop_action_btn.text = f"BUY: {skin['price']} C"
            self.shop_action_btn.bg_color = (200, 150, 40)

    def handle_shop_action(self):
        high_score = 0
        for v in self.save_manager.data.get("high_scores", {}).values():
            if v > high_score: high_score = v
            
        success, msg = self.shop_manager.buy_skin(self.shop_skin_index, high_score)
        
        if not success and msg.startswith("Need"):
            self.shop_action_btn.bg_color = (200, 50, 50)
            self.shop_action_btn.text = msg
            return # Skip update so error text stays
            
        self.update_shop_action_btn()

    def process_xp(self):
        xp_earned = self.score
        if xp_earned == 0: return
        self.save_manager.data["xp"] = self.save_manager.data.get("xp", 0) + xp_earned
        
        while True:
            level = self.save_manager.data.get("player_level", 1)
            xp_needed = level * 500
            if self.save_manager.data["xp"] >= xp_needed:
                self.save_manager.data["xp"] -= xp_needed
                self.save_manager.data["player_level"] = level + 1
            else:
                break
        self.save_manager.save()

    def open_world_map(self):
        self.state = "WORLD_MAP"
        self.level_nodes = []
        unlocked = self.save_manager.data.get("unlocked_levels", 1)
        
        # Show up to 50 levels ahead
        total_to_show = unlocked + 50
        
        positions = []
        import math
        start_y = 150
        spacing_y = 90
        
        # Organic winding vertical path (like a snake body)
        for i in range(total_to_show):
            y = start_y + i * spacing_y
            # Sine wave for winding, with increasing amplitude for flair
            x = (WIDTH // 2) + math.sin(i * 0.8) * 180
            positions.append((x, y))
        
        for i, pos in enumerate(positions):
            level_num = i + 1
            if level_num < unlocked: status = "COMPLETED"
            elif level_num == unlocked: status = "CURRENT"
            else: status = "LOCKED"
            
            btn = LevelNodeButton(pos[0], pos[1], 35, level_num, status, self.title_font)
            btn.original_y = btn.rect.y
            self.level_nodes.append(btn)
            
        # Center the camera on the CURRENT level
        current_y = positions[unlocked - 1][1]
        self.map_scroll_y = max(0, current_y - (HEIGHT // 2))
        
        # Reposition the back button to be small and in the bottom left
        self.map_back_btn = Button(20, HEIGHT - 70, 160, 50, "BACK", self.btn_font, (80, 80, 80), (120, 120, 120))

    def load_level(self, level_num):
        # Keep snake size between levels
        if hasattr(self, 'snake') and self.score > 0 and self.state != "GAME_OVER":
            self.pending_growth = getattr(self, 'pending_growth', 0) + max(0, len(self.snake) - 3)
            
        self.current_level_num = level_num
        self.current_level_data = self.level_manager.get_level(level_num, self.settings.difficulty)
        
        skin = self.shop_manager.get_equipped_skin()
        
        self.snake_head_color = skin["head"]
        self.snake_body_color = skin["body"]
        self.snake_effect = skin.get("effect", "none")
        
        # Keep procedural colors only if they intentionally chose default classic green
        if skin["id"] == "green":
            self.snake_head_color = self.current_level_data["snake_head"]
            self.snake_body_color = self.current_level_data["snake_body"]
            
        self.snake = [[5, 5], [4, 5], [3, 5]]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        
        # Safe Zone: Remove any walls right in front of the starting position so it's easier
        safe_zone = [[x, y] for x in range(3, 16) for y in range(3, 8)]
        self.map_obstacles = [obs for obs in self.current_level_data["obstacles"] if obs not in safe_zone]
        
        self.is_bonus_phase = False
        self.bonus_food = None
        self.bonus_timer = 0
        
        self.food_eaten_this_level = 0
        self.survival_frames = 0
        self.double_score_timer = 0
        self.food_type = "normal"
        self.floating_texts = []
        self.coin_active = False
        self.coin_pos = [-10, -10]
        self.coin_cooldown = random.randint(180, 300)
        
        self.powerup_manager.reset()
        self.combo_count = 0
        self.combo_timer = 0
        
        # Lower overall speed slightly based on user request
        speed_mod = {0: -3, 1: 0, 2: 4}[self.settings.difficulty]
        self.move_delay = max(40, 180 - (self.current_level_data["speed"] + speed_mod) * 3)
        
        self.last_move = pygame.time.get_ticks()
        self.spawn_food()

    def start_game(self):
        self.score = 0
        self.particle_system.particles = []
        self.pending_growth = 0
        self.load_level(1)
        self.state = "PLAYING"

    def spawn_food(self):
        min_x, max_x = (3, COLS - 4) if self.current_level_num in [2, 5] else (0, COLS - 1)
        min_y, max_y = (3, ROWS - 4) if self.current_level_num in [2, 5] else (0, ROWS - 1)
        
        while True:
            self.food = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
            if self.food not in self.snake and self.food not in self.map_obstacles and getattr(self, 'coin_pos', [-1,-1]) != self.food:
                break
                
        rand = random.random()
        self.food_type = "normal"
        if self.current_level_num >= 2 and rand < 0.10:
            self.food_type = "golden"
        elif self.current_level_num >= 3 and 0.10 <= rand < 0.20:
            self.food_type = "bonus"
        elif self.current_level_num >= 4 and 0.20 <= rand < 0.35:
            self.food_type = "poison"

    def spawn_bonus_food(self):
        min_x, max_x = (3, COLS - 4) if self.current_level_num in [2, 5] else (2, COLS - 3)
        min_y, max_y = (3, ROWS - 4) if self.current_level_num in [2, 5] else (2, ROWS - 3)
        while True:
            self.bonus_food = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
            if self.bonus_food not in self.snake and self.bonus_food not in self.map_obstacles:
                break
        self.bonus_timer = 300  # 5 seconds at 60 FPS
        self.food = [-10, -10]  # Hide regular food off-screen

    def spawn_coin(self):
        min_x, max_x = (3, COLS - 4) if self.current_level_num in [2, 5] else (1, COLS - 2)
        min_y, max_y = (3, ROWS - 4) if self.current_level_num in [2, 5] else (1, ROWS - 2)
        while True:
            pos = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
            if pos not in self.snake and pos not in self.map_obstacles and pos != self.food:
                self.coin_pos = pos
                break
        self.coin_active = True
        self.coin_timer = 400 # ~6.5 seconds

    def events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Update buttons based on state for hover animations
        if self.state == "MAIN_MENU":
            self.play_btn.update(mouse_pos)
            self.settings_btn.update(mouse_pos)
            self.shop_btn.update(mouse_pos)
            self.quit_btn.update(mouse_pos)
        elif self.state == "SHOP":
            self.shop_prev_btn.update(mouse_pos)
            self.shop_next_btn.update(mouse_pos)
            self.shop_action_btn.update(mouse_pos)
            self.shop_back_btn.update(mouse_pos)
        elif self.state == "SETTINGS":
            self.sound_btn.update(mouse_pos)
            self.music_btn.update(mouse_pos)
            self.diff_btn.update(mouse_pos)
            self.skin_btn.update(mouse_pos)
            self.back_btn.update(mouse_pos)
        elif self.state == "WORLD_MAP":
            self.map_back_btn.update(mouse_pos)
            for btn in self.level_nodes:
                btn.update(mouse_pos)
        elif self.state == "PAUSED":
            self.resume_btn.update(mouse_pos)
            self.map_btn.update(mouse_pos)
            self.menu_btn.update(mouse_pos)
            self.full_icon_btn.update(mouse_pos)
            self.min_icon_btn.update(mouse_pos)
        elif self.state == "PLAYING":
            self.pause_icon_btn.update(mouse_pos)
            self.full_icon_btn.update(mouse_pos)
            self.min_icon_btn.update(mouse_pos)
        elif self.state == "GAME_OVER":
            self.retry_btn.update(mouse_pos)
            self.map_btn.update(mouse_pos)
            self.menu_btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEWHEEL and self.state == "WORLD_MAP":
                self.map_scroll_y -= event.y * 50
                max_scroll = max(0, self.level_nodes[-1].original_y - HEIGHT + 150)
                self.map_scroll_y = max(0, min(self.map_scroll_y, max_scroll))
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.swipe_start = event.pos
                if self.state == "WORLD_MAP":
                    self.is_map_dragging = True
                    
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.state == "WORLD_MAP":
                    self.is_map_dragging = False
                
                # Swipe detection for snake movement
                if self.swipe_start and self.state == "PLAYING":
                    dx = event.pos[0] - self.swipe_start[0]
                    dy = event.pos[1] - self.swipe_start[1]
                    if abs(dx) > 20 or abs(dy) > 20:
                        if abs(dx) > abs(dy):
                            if dx > 0 and self.direction != "LEFT": self.next_direction = "RIGHT"
                            elif dx < 0 and self.direction != "RIGHT": self.next_direction = "LEFT"
                        else:
                            if dy > 0 and self.direction != "UP": self.next_direction = "DOWN"
                            elif dy < 0 and self.direction != "DOWN": self.next_direction = "UP"
                self.swipe_start = None
                
            if event.type == pygame.MOUSEMOTION and self.is_map_dragging and self.state == "WORLD_MAP":
                self.map_scroll_y -= event.rel[1]
                max_scroll = max(0, self.level_nodes[-1].original_y - HEIGHT + 150)
                self.map_scroll_y = max(0, min(self.map_scroll_y, max_scroll))
            
            # Handle UI Clicks
            if self.state == "MAIN_MENU":
                if self.play_btn.handle_event(event): self.open_world_map()
                if self.settings_btn.handle_event(event): self.state = "SETTINGS"
                if self.shop_btn.handle_event(event):
                    self.state = "SHOP"
                    self.update_shop_action_btn()
                if self.quit_btn.handle_event(event): self.running = False
                    
            elif self.state == "SHOP":
                if self.shop_prev_btn.handle_event(event):
                    self.shop_skin_index = (self.shop_skin_index - 1) % len(shop.SKIN_CATALOG)
                    self.update_shop_action_btn()
                if self.shop_next_btn.handle_event(event):
                    self.shop_skin_index = (self.shop_skin_index + 1) % len(shop.SKIN_CATALOG)
                    self.update_shop_action_btn()
                if self.shop_action_btn.handle_event(event):
                    self.handle_shop_action()
                if self.shop_back_btn.handle_event(event):
                    self.state = "MAIN_MENU"
                    
            elif self.state == "SETTINGS":
                if self.sound_btn.handle_event(event):
                    self.settings.sound_enabled = not self.settings.sound_enabled
                    self.update_settings_btn_text()
                    self.settings.save_settings()
                if self.music_btn.handle_event(event):
                    self.settings.music_enabled = not self.settings.music_enabled
                    if self.settings.music_enabled:
                        try:
                            pygame.mixer.music.play(-1)
                        except: pass
                    else:
                        try:
                            pygame.mixer.music.stop()
                        except: pass
                    self.update_settings_btn_text()
                    self.settings.save_settings()
                if self.diff_btn.handle_event(event):
                    self.settings.difficulty = (self.settings.difficulty + 1) % 3
                    self.update_settings_btn_text()
                    self.settings.save_settings()
                if self.skin_btn.handle_event(event):
                    self.settings.skin = (getattr(self.settings, 'skin', 0) + 1) % 4
                    self.update_settings_btn_text()
                    self.settings.save_settings()
                if self.back_btn.handle_event(event):
                    self.state = "MAIN_MENU"
                    
            elif self.state == "WORLD_MAP":
                if self.map_back_btn.handle_event(event):
                    self.state = "MAIN_MENU"
                for btn in self.level_nodes:
                    if btn.handle_event(event):
                        self.score = 0
                        self.particle_system.particles = []
                        self.pending_growth = 0
                        self.load_level(btn.level_num)
                        self.state = "PLAYING"
                    
            elif self.state == "PAUSED":
                if self.resume_btn.handle_event(event): self.state = "PLAYING"
                if self.map_btn.handle_event(event): self.open_world_map()
                if self.menu_btn.handle_event(event): self.state = "MAIN_MENU"
                if self.full_icon_btn.handle_event(event): self.toggle_fullscreen()
                if self.min_icon_btn.handle_event(event): pygame.display.iconify()
                    
            elif self.state == "PLAYING":
                if self.pause_icon_btn.handle_event(event): self.state = "PAUSED"
                if self.full_icon_btn.handle_event(event): self.toggle_fullscreen()
                if self.min_icon_btn.handle_event(event): pygame.display.iconify()
                    
            elif self.state == "GAME_OVER":
                if self.retry_btn.handle_event(event): self.start_game()
                if self.map_btn.handle_event(event): self.open_world_map()
                if self.menu_btn.handle_event(event): self.state = "MAIN_MENU"
            
            # Handle Keyboard Shortcuts
            if event.type == pygame.KEYDOWN:
                # Fullscreen Toggle (F or F11)
                if event.key == pygame.K_f or event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                
                # ESC Handling (Exit fullscreen first, otherwise toggle pause)
                elif event.key == pygame.K_ESCAPE:
                    if self.settings.fullscreen:
                        self.toggle_fullscreen()
                    else:
                        if self.state == "PLAYING":
                            self.state = "PAUSED"
                        elif self.state == "PAUSED":
                            self.state = "PLAYING"

                # Pause / Resume (P or SPACE)
                elif event.key in (pygame.K_p, pygame.K_SPACE):
                    if self.state == "PLAYING":
                        self.state = "PAUSED"
                    elif self.state == "PAUSED":
                        self.state = "PLAYING"
                
                # Snake Movement
                if self.state == "PLAYING":
                    if event.key == pygame.K_UP and self.direction != "DOWN": self.next_direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP": self.next_direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT": self.next_direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT": self.next_direction = "RIGHT"

    def check_objective(self):
        obj_type = self.current_level_data.get("objective_type", "score")
        obj_val = self.current_level_data.get("objective_value", 50)
        
        if obj_type == "score" and self.score >= obj_val:
            return True
        if obj_type == "collect_food" and self.food_eaten_this_level >= obj_val:
            return True
        if obj_type == "survival" and (self.survival_frames // FPS) >= obj_val:
            return True
        return False

    def update(self):
        # Update background stars for all states
        for star in self.stars: star["phase"] += 1

        if self.state == "LEVEL_TRANSITION":
            self.transition_timer -= 1
            # Mid-point of fade transition: Load the next level while screen is totally black
            if self.transition_timer == 45:
                # Load new level right in the middle of transition
                self.load_level(self.current_level_num + 1)
            
            if self.transition_timer <= 0:
                self.state = "PLAYING"
            return

        if self.state != "PLAYING": return
        
        if getattr(self, 'double_score_timer', 0) > 0:
            self.double_score_timer -= 1
            
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0
                
        self.powerup_manager.update()
        if not self.powerup_manager.active_powerup and self.powerup_manager.spawn_timer == 0:
            self.powerup_manager.spawn(COLS, ROWS, self.map_obstacles, self.snake, self.food, self.coin_pos)
            
        # Magnet effect
        if "MAGNET" in self.powerup_manager.active_buffs and self.coin_active:
            # Move coin 1 block towards head every 10 frames
            if pygame.time.get_ticks() % 10 == 0:
                hx, hy = self.snake[0]
                cx, cy = self.coin_pos
                if hx > cx and [cx+1, cy] not in self.map_obstacles: self.coin_pos[0] += 1
                elif hx < cx and [cx-1, cy] not in self.map_obstacles: self.coin_pos[0] -= 1
                elif hy > cy and [cx, cy+1] not in self.map_obstacles: self.coin_pos[1] += 1
                elif hy < cy and [cx, cy-1] not in self.map_obstacles: self.coin_pos[1] -= 1
        
        # Floating Texts update
        for ft in self.floating_texts:
            ft["y"] -= 1.5
            ft["life"] -= 1
        self.floating_texts = [ft for ft in self.floating_texts if ft["life"] > 0]

        if not self.is_bonus_phase:
            self.survival_frames += 1
            if self.current_level_data.get("objective_type") == "survival" and self.check_objective():
                self.is_bonus_phase = True
                self.spawn_bonus_food()
                
            # Coin Spawning Logic
            if not self.coin_active:
                if self.coin_cooldown > 0:
                    self.coin_cooldown -= 1
                else:
                    self.spawn_coin()
            else:
                self.coin_timer -= 1
                if self.coin_timer <= 0:
                    self.coin_active = False
                    self.coin_cooldown = random.randint(200, 400)

        # Food Animation logic
        if self.food_grow:
            self.food_scale += 0.02
            if self.food_scale >= 1.25: self.food_grow = False
        else:
            self.food_scale -= 0.02
            if self.food_scale <= 0.85: self.food_grow = True

        # Particles Update
        self.particle_system.update()
        
        # Skin Effects
        if hasattr(self, 'snake_effect') and self.snake_effect != "none" and len(self.snake) > 0:
            if random.random() < 0.4:
                segment = random.choice(self.snake)
                sx = segment[0] * BLOCK + BLOCK // 2
                sy = segment[1] * BLOCK + BLOCK // 2
                if self.snake_effect == "fire":
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-1, 1), "vy": random.uniform(-2, 0), "life": 20, "color": (255, random.randint(50, 150), 0), "size": random.randint(2, 5)})
                elif self.snake_effect == "electric":
                    if random.random() < 0.5:
                        self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-2, 2), "vy": random.uniform(-2, 2), "life": 10, "color": (0, 255, 255), "size": random.randint(1, 3)})
                elif self.snake_effect == "toxic":
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-0.5, 0.5), "vy": random.uniform(-1, 1), "life": 30, "color": (100, 255, 50), "size": random.randint(2, 6)})
                elif self.snake_effect in ["glow", "cyber"]:
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": 0, "vy": 0, "life": 15, "color": self.snake_head_color, "size": random.randint(4, 8)})
                elif self.snake_effect == "ice":
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-1, 1), "vy": random.uniform(0, 2), "life": 25, "color": (200, 240, 255), "size": random.randint(2, 4)})
                elif self.snake_effect == "galaxy":
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-1, 1), "vy": random.uniform(-1, 1), "life": 40, "color": (255, 255, 255), "size": random.randint(1, 2)})
                elif self.snake_effect == "shadow":
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-1, 1), "vy": random.uniform(-1, 1), "life": 30, "color": (10, 10, 10), "size": random.randint(3, 6)})
                elif self.snake_effect in ["sparkle", "gold_sparkle"]:
                    c = (255, 255, 255) if self.snake_effect == "sparkle" else (255, 215, 0)
                    self.particle_system.particles.append({"x": sx, "y": sy, "vx": random.uniform(-0.5, 0.5), "vy": random.uniform(-0.5, 0.5), "life": 15, "color": c, "size": random.randint(1, 3)})

        current_time = pygame.time.get_ticks()
        active_delay = self.move_delay
        if "SPEED" in self.powerup_manager.active_buffs: active_delay //= 2
        if "SLOW" in self.powerup_manager.active_buffs: active_delay = int(active_delay * 1.5)

        if current_time - self.last_move < active_delay: return
        self.last_move = current_time

        self.direction = self.next_direction
        head = self.snake[0].copy()

        if self.direction == "RIGHT": head[0] += 1
        elif self.direction == "LEFT": head[0] -= 1
        elif self.direction == "UP": head[1] -= 1
        elif self.direction == "DOWN": head[1] += 1

        # Bonus Timer Update
        if self.is_bonus_phase:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                # Timer ran out, move to next level without bonus
                self.process_xp()
                # Unlock next level
                next_unlocked = self.current_level_num + 1
                if next_unlocked > self.save_manager.data.get("unlocked_levels", 1):
                    self.save_manager.data["unlocked_levels"] = next_unlocked
                    self.save_manager.save()
                
                self.is_bonus_phase = False
                self.state = "LEVEL_TRANSITION"
                self.transition_timer = 90

        # Collisions (Walls, Self, Obstacles)
        if (head[0] < 0 or head[0] >= COLS or head[1] < 0 or head[1] >= ROWS or 
            head in self.snake or head in self.map_obstacles):
            if self.powerup_manager.has_shield:
                self.powerup_manager.has_shield = False
                self.audio_manager.play_sound("eat") # Pop shield sound
                # Rewind head back to safe spot and skip turn
                self.floating_texts.append({"x": head[0]*BLOCK, "y": head[1]*BLOCK, "text": "SHIELD POP!", "color": (50, 100, 255), "life": 45})
                return
            else:
                self.process_xp()
                self.state = "GAME_OVER"
                self.save_manager.save_high_score(self.current_level_num, self.score)
                self.audio_manager.play_sound("gameover")
                return

        self.snake.insert(0, head)

        # Powerup Collision
        if self.powerup_manager.active_powerup and head == self.powerup_manager.active_pos:
            ptype = self.powerup_manager.collect()
            self.audio_manager.play_sound("eat")
            self.floating_texts.append({"x": head[0]*BLOCK, "y": head[1]*BLOCK, "text": f"{ptype}!", "color": POWERUP_COLORS[ptype], "life": 45})

        # Eating logic
        if not self.is_bonus_phase and head == self.food:
            self.combo_count += 1
            self.combo_timer = 300 # 5 seconds
            
            mult = 2 if getattr(self, 'double_score_timer', 0) > 0 else 1
            combo_mult = 1 + (self.combo_count // 3)
            total_mult = mult * combo_mult
            
            fx_x, fx_y = self.food[0] * BLOCK + BLOCK // 2, self.food[1] * BLOCK
            
            if self.food_type == "normal":
                pts = 10 * total_mult
                self.score += pts
                self.food_eaten_this_level += 1
                color = self.current_level_data["food_color"]
                self.floating_texts.append({"x": fx_x, "y": fx_y, "text": f"+{pts}", "color": (255,255,255), "life": 30})
                
            elif self.food_type == "golden":
                pts = 30 * total_mult
                self.score += pts
                self.save_manager.data["coins"] += 5
                self.save_manager.save()
                self.food_eaten_this_level += 1
                color = (255, 215, 0)
                self.floating_texts.append({"x": fx_x, "y": fx_y, "text": f"+{pts} & +5 COINS", "color": color, "life": 45})
                
            elif self.food_type == "bonus":
                self.double_score_timer = 600 # 10 seconds
                self.food_eaten_this_level += 1
                color = (50, 255, 255)
                self.floating_texts.append({"x": fx_x, "y": fx_y, "text": "2X SCORE!", "color": color, "life": 45})
                
            elif self.food_type == "poison":
                self.combo_count = 0 # Break combo
                self.score = max(0, self.score - 20)
                color = (150, 50, 200)
                self.floating_texts.append({"x": fx_x, "y": fx_y, "text": "-20 POISON!", "color": (255, 50, 50), "life": 45})

            self.particle_system.emit_food_particles(self.food, color)
            self.save_manager.save_high_score(self.current_level_num, self.score)
            self.audio_manager.play_sound("eat")
            
            # Trigger Bonus Phase
            if self.check_objective():
                self.is_bonus_phase = True
                self.spawn_bonus_food()
            else:
                self.spawn_food()
                
        elif self.coin_active and head == self.coin_pos:
            self.save_manager.data["coins"] += 10
            self.save_manager.save()
            self.audio_manager.play_sound("coin")
            self.coin_active = False
            self.coin_cooldown = random.randint(300, 600)
            self.floating_texts.append({
                "x": self.coin_pos[0] * BLOCK + BLOCK//2,
                "y": self.coin_pos[1] * BLOCK,
                "text": "+10",
                "color": (255, 215, 0),
                "life": 45
            })
                
        elif self.is_bonus_phase and head == self.bonus_food:
            # Ate the big bonus food!
            self.score += 50
            self.particle_system.emit_food_particles(self.bonus_food, (255, 215, 0), count=35)
            self.save_manager.save_high_score(self.current_level_num, self.score)
            self.audio_manager.play_sound("eat")
            
            self.process_xp()
            
            # Unlock next level
            next_unlocked = self.current_level_num + 1
            if next_unlocked > self.save_manager.data.get("unlocked_levels", 1):
                self.save_manager.data["unlocked_levels"] = next_unlocked
                self.save_manager.save()
            
            self.is_bonus_phase = False
            self.state = "LEVEL_TRANSITION"
            self.transition_timer = 90
        else:
            # Snake maintains its length by growing if pending
            if getattr(self, 'pending_growth', 0) > 0:
                self.pending_growth -= 1
            else:
                self.snake.pop()

    def draw_background(self, color):
        self.screen.fill(color)
        # Twinkling stars
        for star in self.stars:
            star_alpha = 120 + int(40 * abs(__import__('math').sin(star['phase'] * 0.1)))
            pygame.draw.circle(self.screen, (star_alpha, star_alpha, star_alpha), (star["x"], star["y"]), star["size"])
            
        # Grid lines for subtle professional feel
        for x in range(0, WIDTH, BLOCK):
            pygame.draw.line(self.screen, (color[0]+15, color[1]+15, color[2]+15), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, BLOCK):
            pygame.draw.line(self.screen, (color[0]+15, color[1]+15, color[2]+15), (0, y), (WIDTH, y))

    def draw(self):
        # Draw base environment
        if self.state == "MAIN_MENU":
            self.draw_background((30, 45, 65)) # Kid-friendly soft blue
        elif self.state == "SETTINGS":
            self.draw_background((20, 25, 35))
        elif self.state == "WORLD_MAP":
            self.draw_background((25, 35, 50))
        else:
            self.draw_background(self.current_level_data["bg_color"])

        if self.state == "MAIN_MENU":
            import math
            time_tick = pygame.time.get_ticks()
            
            # Moving 3D-like grid
            offset = (time_tick // 30) % 40
            for x in range(0, WIDTH + 1, 40):
                pygame.draw.line(self.screen, (20, 30, 50), (x, 0), (x, HEIGHT), 1)
            for y in range(-40, HEIGHT + 1, 40):
                pygame.draw.line(self.screen, (20, 30, 50), (0, y + offset), (WIDTH, y + offset), 1)

            # Draw ambient glowing particles
            for p in self.bg_particles:
                p["y"] -= p["speed"]
                if p["y"] < 0:
                    p["y"] = HEIGHT
                    p["x"] = random.randint(0, WIDTH)
                pygame.draw.circle(self.screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])
                pygame.draw.circle(self.screen, (255, 255, 255), (int(p["x"]), int(p["y"])), max(1, p["size"]-2))

            # Decorative Snake crawling in background
            cx, cy = WIDTH // 2, HEIGHT // 2 + 30
            radius = 220
            snake_length = 20
            for i in range(snake_length):
                angle = (time_tick * 0.001) - (i * 0.08)
                sx = cx + math.cos(angle) * radius
                sy = cy + math.sin(angle * 2.0) * (radius * 0.4)
                s_radius = max(3, 12 - i * 0.4)
                color = (0, 200, 100) if i > 0 else (0, 255, 120)
                pygame.draw.circle(self.screen, color, (int(sx), int(sy)), int(s_radius))
                if i == 0: # Eyes
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(sx)-3, int(sy)-3), 3)
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(sx)+3, int(sy)-3), 3)

            # Neon Title
            title_text = "ADVANCED SNAKE"
            base_x = WIDTH // 2 - (len(title_text) * 23) // 2 + 5
            for i, char in enumerate(title_text):
                y_offset = math.sin(time_tick * 0.004 + i * 0.4) * 8
                
                # Glow layers
                for g in range(3, 0, -1):
                    glow = self.title_font.render(char, True, (0, 200, 255))
                    glow.set_alpha(150 // g)
                    self.screen.blit(glow, (base_x + i * 24 - g, 70 + y_offset - g))
                
                char_surf = self.title_font.render(char, True, (255, 255, 255))
                self.screen.blit(char_surf, (base_x + i * 24, 70 + y_offset))
            
            self.play_btn.draw(self.screen)
            self.settings_btn.draw(self.screen)
            self.shop_btn.draw(self.screen)
            self.quit_btn.draw(self.screen)
            
            # Draw XP and Level
            level = self.save_manager.data.get("player_level", 1)
            xp = self.save_manager.data.get("xp", 0)
            xp_needed = level * 500
            
            draw_text(self.screen, f"Player Level {level}", self.btn_font, (255, 215, 0), (WIDTH//2, HEIGHT - 110))
            
            # XP Bar
            bar_w = 300
            bar_h = 20
            bar_x = WIDTH//2 - bar_w//2
            bar_y = HEIGHT - 80
            pygame.draw.rect(self.screen, (50,50,50), (bar_x, bar_y, bar_w, bar_h))
            if xp_needed > 0:
                pygame.draw.rect(self.screen, (100, 200, 255), (bar_x, bar_y, int(bar_w * (xp/xp_needed)), bar_h))
            pygame.draw.rect(self.screen, (255,255,255), (bar_x, bar_y, bar_w, bar_h), 2)
            draw_text(self.screen, f"{xp} / {xp_needed} XP", self.hud_font, (255,255,255), (WIDTH//2, bar_y + bar_h//2 + 2))
            
        elif self.state == "SHOP":
            draw_text(self.screen, "SKIN SHOP", self.title_font, (255,215,0), (WIDTH//2, 40))
            draw_text(self.screen, f"🪙 COINS: {self.save_manager.data.get('coins', 0)}", self.btn_font, (255,215,0), (WIDTH//2, 80))
            
            skin = self.shop_manager.get_skin(self.shop_skin_index)
            
            # --- Snake Preview Box ---
            box_rect = pygame.Rect(WIDTH//2 - 150, 110, 300, 120)
            pygame.draw.rect(self.screen, (20, 25, 40), box_rect, border_radius=10)
            pygame.draw.rect(self.screen, shop.RARITY_COLORS[skin["rarity"]], box_rect, width=2, border_radius=10)
            
            cx, cy = WIDTH//2, 170
            
            # Simulated snake body
            pygame.draw.rect(self.screen, skin["body"], (cx-50, cy-15, 80, 30), border_radius=15)
            # Head
            pygame.draw.circle(self.screen, skin["head"], (cx+20, cy), 18)
            # Eyes
            pygame.draw.circle(self.screen, (255,255,255), (cx+25, cy-6), 6)
            pygame.draw.circle(self.screen, (255,255,255), (cx+25, cy+6), 6)
            pygame.draw.circle(self.screen, (0,0,0), (cx+27, cy-6), 3)
            pygame.draw.circle(self.screen, (0,0,0), (cx+27, cy+6), 3)
            
            # --- Skin Details ---
            draw_text(self.screen, skin["name"], self.title_font, (255,255,255), (WIDTH//2, 260))
            
            # Rarity
            rarity_col = shop.RARITY_COLORS[skin["rarity"]]
            stars = "★" * (["COMMON", "RARE", "EPIC", "LEGENDARY"].index(skin["rarity"]) + 1)
            draw_text(self.screen, f"{stars} {skin['rarity']}", self.btn_font, rarity_col, (WIDTH//2, 290))
            
            # Description
            desc_font = pygame.font.SysFont("Arial", 18, italic=True)
            draw_text(self.screen, f"\"{skin['desc']}\"", desc_font, (180, 180, 180), (WIDTH//2, 320))
            
            # Index / Navigation
            draw_text(self.screen, f"Skin {self.shop_skin_index + 1} / {len(shop.SKIN_CATALOG)}", self.hud_font, (200, 200, 200), (WIDTH//2, 430))
            
            self.shop_prev_btn.rect.centery = 430
            self.shop_next_btn.rect.centery = 430
            
            # Action button is already positioned correctly (350), let's move it down a bit to fit details
            self.shop_action_btn.rect.centery = 370
            self.shop_back_btn.rect.centery = 490
            
            self.shop_prev_btn.draw(self.screen)
            self.shop_next_btn.draw(self.screen)
            self.shop_action_btn.draw(self.screen)
            self.shop_back_btn.draw(self.screen)
            
        elif self.state == "SETTINGS":
            draw_text(self.screen, "SETTINGS", self.title_font, (255, 255, 255), (WIDTH//2, 60))
            self.sound_btn.draw(self.screen)
            self.music_btn.draw(self.screen)
            self.diff_btn.draw(self.screen)
            self.skin_btn.draw(self.screen)
            self.back_btn.draw(self.screen)
            
        elif self.state == "WORLD_MAP":
            # Draw path lines
            for i in range(len(self.level_nodes) - 1):
                p1 = (self.level_nodes[i].rect.centerx, self.level_nodes[i].original_y + self.level_nodes[i].rect.height//2 - self.map_scroll_y)
                p2 = (self.level_nodes[i+1].rect.centerx, self.level_nodes[i+1].original_y + self.level_nodes[i+1].rect.height//2 - self.map_scroll_y)
                
                # If level is unlocked/completed, color path green
                if self.level_nodes[i+1].status != "LOCKED":
                    color = (46, 204, 113)
                else:
                    color = (100, 100, 100)
                pygame.draw.line(self.screen, color, p1, p2, 6)
                
            for btn in self.level_nodes:
                btn.rect.y = btn.original_y - self.map_scroll_y
                btn.draw(self.screen)
                
            # --- HUD Overlay ---
            # Top gradient / solid bar for Title + Stats
            pygame.draw.rect(self.screen, (20, 25, 40), (0, 0, WIDTH, 80))
            pygame.draw.rect(self.screen, (0, 255, 120), (0, 78, WIDTH, 2)) # sleek border line
            
            draw_text(self.screen, "WORLD MAP", self.title_font, (255, 255, 255), (WIDTH//2, 40))
            
            # Show Coins
            coins = self.save_manager.data.get("coins", 0)
            draw_text(self.screen, f"Coins: {coins}", self.hud_font, (255, 215, 0), (WIDTH - 80, 40))
            
            # Show Player Level
            lvl = self.save_manager.data.get("player_level", 1)
            draw_text(self.screen, f"Player Lv: {lvl}", self.hud_font, (100, 200, 255), (80, 40))
            
            # Back Button (Bottom Left)
            self.map_back_btn.draw(self.screen)
            
        elif self.state in ["PLAYING", "PAUSED", "GAME_OVER", "LEVEL_TRANSITION"]:
            # Draw Obstacles
            for obs in self.map_obstacles:
                pygame.draw.rect(self.screen, (100, 100, 110), (obs[0]*BLOCK, obs[1]*BLOCK, BLOCK, BLOCK), border_radius=4)
                
            # Draw Regular Food or Bonus Food
            if not self.is_bonus_phase:
                center = (self.food[0] * BLOCK + BLOCK // 2, self.food[1] * BLOCK + BLOCK // 2)
                radius = int((BLOCK // 2 - 2) * self.food_scale)
                
                if self.food_type == "normal":
                    if self.apple_image:
                        r = self.apple_image.get_rect(center=center)
                        self.screen.blit(self.apple_image, r)
                    else:
                        fc = self.current_level_data["food_color"]
                        pygame.draw.circle(self.screen, (max(0, fc[0]-100), max(0, fc[1]-100), max(0, fc[2]-100)), center, radius + 4)
                        pygame.draw.circle(self.screen, fc, center, radius)
                        pygame.draw.circle(self.screen, (255, 255, 255), (center[0]-3, center[1]-3), 2)
                elif self.food_type == "golden":
                    pygame.draw.circle(self.screen, (200, 150, 0), center, radius + 4)
                    pygame.draw.circle(self.screen, (255, 215, 0), center, radius)
                    pygame.draw.circle(self.screen, (255, 255, 255), (center[0]-2, center[1]-2), 3)
                elif self.food_type == "bonus":
                    pygame.draw.circle(self.screen, (0, 150, 200), center, radius + 4)
                    pygame.draw.circle(self.screen, (50, 200, 255), center, radius)
                    pygame.draw.circle(self.screen, (255, 255, 255), (center[0]-2, center[1]-2), 3)
                elif self.food_type == "poison":
                    pygame.draw.circle(self.screen, (100, 20, 150), center, radius + 2)
                    pygame.draw.circle(self.screen, (200, 40, 40), center, radius - 2)
            else:
                # Draw Huge Bonus Food
                b_center = (self.bonus_food[0] * BLOCK + BLOCK // 2, self.bonus_food[1] * BLOCK + BLOCK // 2)
                pulse = abs(__import__('math').sin(pygame.time.get_ticks() * 0.005))
                b_radius = int((BLOCK // 2 + 5) + pulse * 6)
                
                # Glowing Gold
                pygame.draw.circle(self.screen, (200, 150, 0), b_center, b_radius + 6)
                pygame.draw.circle(self.screen, (255, 215, 0), b_center, b_radius)
                pygame.draw.circle(self.screen, (255, 255, 255), (b_center[0]-4, b_center[1]-4), 4)
                
                # Top-Right Timer Progress Box
                box_w = 200
                box_h = 28
                box_x = WIDTH - box_w - 20
                box_y = 60 # Just below the High Score HUD
                
                # Calculate progress
                max_time = 300.0 # 5 seconds
                progress = max(0, self.bonus_timer / max_time)
                fill_w = int(box_w * progress)
                
                # Color transitions from Green to Red
                if progress > 0.5: bar_color = (50, 255, 50)
                elif progress > 0.25: bar_color = (255, 200, 0)
                else: bar_color = (255, 50, 50)
                
                # Draw Background (Empty space)
                pygame.draw.rect(self.screen, (40, 40, 40), (box_x, box_y, box_w, box_h), border_radius=6)
                # Draw Fill (Time left)
                if fill_w > 0:
                    pygame.draw.rect(self.screen, bar_color, (box_x, box_y, fill_w, box_h), border_radius=6)
                # Draw Border
                pygame.draw.rect(self.screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 2, border_radius=6)
                
                # Draw Text Inside Box
                sec_left = (self.bonus_timer // 60) + 1
                text_col = (255, 255, 255) if progress < 0.25 else (0, 0, 0)
                draw_text(self.screen, f"BONUS: {sec_left}s", self.hud_font, text_col, (box_x + box_w//2, box_y + box_h//2 + 1))

            if self.coin_active:
                cx = self.coin_pos[0] * BLOCK + BLOCK // 2
                cy = self.coin_pos[1] * BLOCK + BLOCK // 2
                width_scale = abs(__import__('math').cos(pygame.time.get_ticks() * 0.005))
                w = int(20 * width_scale)
                if w < 2: w = 2
                pygame.draw.ellipse(self.screen, (255, 215, 0), (cx - w//2, cy - 10, w, 20))
                pygame.draw.ellipse(self.screen, (200, 150, 0), (cx - w//2, cy - 10, w, 20), 2)
                
            # Draw Powerup
            if self.powerup_manager.active_powerup:
                px = self.powerup_manager.active_pos[0] * BLOCK + BLOCK//2
                py = self.powerup_manager.active_pos[1] * BLOCK + BLOCK//2
                color = POWERUP_COLORS[self.powerup_manager.active_powerup]
                
                sz = 12
                pts = [(px, py-sz), (px+sz, py), (px, py+sz), (px-sz, py)]
                pygame.draw.polygon(self.screen, color, pts)
                pygame.draw.polygon(self.screen, (255,255,255), pts, 2)

            # Draw Particles
            self.particle_system.draw(self.screen)

            head_color = self.snake_head_color
            body_color = self.snake_body_color
            
            if hasattr(self, 'snake_effect') and self.snake_effect == "rainbow":
                time_val = pygame.time.get_ticks() * 0.005
                import math
                r = int(127 + 128 * math.sin(time_val))
                g = int(127 + 128 * math.sin(time_val + 2))
                b = int(127 + 128 * math.sin(time_val + 4))
                head_color = (r, g, b)
                body_color = (max(0, r-50), max(0, g-50), max(0, b-50))
                
            # Professional Classic Tube Design
            radius = int(BLOCK * 0.45)
            
            # Helper to blend colors smoothly from head to tail
            def blend_color(c1, c2, ratio):
                return (int(c1[0] * (1-ratio) + c2[0] * ratio),
                        int(c1[1] * (1-ratio) + c2[1] * ratio),
                        int(c1[2] * (1-ratio) + c2[2] * ratio))

            points = [(s[0] * BLOCK + BLOCK//2, s[1] * BLOCK + BLOCK//2) for s in self.snake]

            # 1. Unified Drop Shadow (Perfect continuous pipe shadow)
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, (20, 20, 20), (points[i][0]+3, points[i][1]+3), (points[i+1][0]+3, points[i+1][1]+3), radius * 2)
            for p in points:
                pygame.draw.circle(self.screen, (20, 20, 20), (p[0]+3, p[1]+3), radius)

            # 2. Main Body (Smooth Gradient Tube)
            for i in range(len(points) - 1):
                ratio = i / max(1, len(points) - 1)
                col = blend_color(head_color, body_color, ratio)
                pygame.draw.line(self.screen, col, points[i], points[i+1], radius * 2)
            
            for i, p in enumerate(points):
                ratio = i / max(1, len(points) - 1)
                col = blend_color(head_color, body_color, ratio)
                pygame.draw.circle(self.screen, col, p, radius)
                
                # Inner Glossy Shine (Makes it look like a 3D glass tube)
                if i > 0:
                    shine_col = blend_color((255, 255, 255), col, 0.35) # Brightened body color
                    shine_radius = max(2, int(radius * 0.3))
                    pygame.draw.circle(self.screen, shine_col, (p[0] - shine_radius, p[1] - shine_radius), shine_radius)

            # 3. Classic Clean Head
            if len(points) > 0:
                hx, hy = points[0]
                pygame.draw.circle(self.screen, head_color, (hx, hy), radius + 2)
                
                # Classic Cute Eyes (Looking in movement direction)
                if self.direction == "UP": e1, e2 = (hx - 4, hy - 4), (hx + 4, hy - 4)
                elif self.direction == "DOWN": e1, e2 = (hx - 4, hy + 4), (hx + 4, hy + 4)
                elif self.direction == "LEFT": e1, e2 = (hx - 4, hy - 4), (hx - 4, hy + 4)
                else: e1, e2 = (hx + 4, hy - 4), (hx + 4, hy + 4)
                
                # Big white eyes
                pygame.draw.circle(self.screen, (255, 255, 255), e1, 4)
                pygame.draw.circle(self.screen, (255, 255, 255), e2, 4)
                
                # Black pupils facing forward
                px, py = 0, 0
                if self.direction == "UP": py = -1
                elif self.direction == "DOWN": py = 1
                elif self.direction == "LEFT": px = -1
                else: px = 1
                pygame.draw.circle(self.screen, (0, 0, 0), (e1[0]+px, e1[1]+py), 2)
                pygame.draw.circle(self.screen, (0, 0, 0), (e2[0]+px, e2[1]+py), 2)

            # Draw HUD
            draw_text(self.screen, f"Score: {self.score}", self.hud_font, (255, 255, 255), (60, 20))
            draw_text(self.screen, f"Level {self.current_level_num}: {self.current_level_data['name']}", self.hud_font, (255, 255, 0), (WIDTH // 2, 20))
            
            # Use SaveManager for high score
            current_hs = self.save_manager.get_high_score(self.current_level_num)
            draw_text(self.screen, f"High Score: {current_hs}", self.hud_font, (255, 255, 255), (WIDTH - 80, 20))
            
            # Objective HUD
            obj_type = self.current_level_data.get("objective_type", "score")
            obj_val = self.current_level_data.get("objective_value", 50)
            
            if obj_type == "score":
                obj_text = f"Goal: {self.score}/{obj_val} Score"
            elif obj_type == "collect_food":
                obj_text = f"Goal: {self.food_eaten_this_level}/{obj_val} Apples"
            elif obj_type == "survival":
                survived = self.survival_frames // FPS
                obj_text = f"Goal: Survive {survived}/{obj_val}s"
            else:
                obj_text = ""
                
            draw_text(self.screen, obj_text, self.hud_font, (0, 255, 255), (WIDTH // 2, 45))
            
            # Coin HUD
            draw_text(self.screen, f"Coins: {self.save_manager.data.get('coins', 0)}", self.hud_font, (255, 215, 0), (60, 45))
            
            # Floating Texts
            for ft in self.floating_texts:
                alpha = max(0, min(255, ft["life"] * 6))
                if alpha > 0:
                    txt_surf = self.hud_font.render(ft["text"], True, ft["color"])
                    txt_surf.set_alpha(alpha)
                    r = txt_surf.get_rect(center=(int(ft["x"]), int(ft["y"])))
                    self.screen.blit(txt_surf, r)
                    
            if getattr(self, 'double_score_timer', 0) > 0:
                sec = self.double_score_timer // FPS
                draw_text(self.screen, f"DOUBLE SCORE: {sec}s", self.hud_font, (50, 255, 255), (WIDTH//2, 70))
                
            if self.combo_count > 0:
                mult = 1 + (self.combo_count // 3)
                txt = f"COMBO x{mult} ({self.combo_count})"
                c_alpha = min(255, self.combo_timer * 2)
                txt_surf = self.hud_font.render(txt, True, (255, 100, 200))
                txt_surf.set_alpha(c_alpha)
                self.screen.blit(txt_surf, txt_surf.get_rect(center=(WIDTH//2, 95)))
                
            # Draw active buffs
            buff_y = 120
            for b in self.powerup_manager.active_buffs:
                sec = self.powerup_manager.active_buffs[b] // FPS
                draw_text(self.screen, f"{b}: {sec}s", self.hud_font, POWERUP_COLORS[b], (WIDTH//2, buff_y))
                buff_y += 20
                
            if self.powerup_manager.has_shield:
                draw_text(self.screen, "SHIELD ACTIVE", self.hud_font, POWERUP_COLORS["SHIELD"], (WIDTH//2, buff_y))
            
            # Draw In-Game Control Buttons
            if self.state == "PLAYING":
                self.pause_icon_btn.draw(self.screen)
            if self.state in ["PLAYING", "PAUSED"]:
                self.full_icon_btn.draw(self.screen)
                self.min_icon_btn.draw(self.screen)

            # Draw State Overlays
            if self.state == "PAUSED":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0,0))
                draw_text(self.screen, "PAUSED", self.title_font, (255, 255, 0), (WIDTH//2, 80))
                self.resume_btn.draw(self.screen)
                self.map_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)
                
            elif self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0,0))
                draw_text(self.screen, "GAME OVER", self.title_font, (255, 60, 60), (WIDTH//2, 80))
                draw_text(self.screen, f"Final Score: {self.score}", self.btn_font, (255, 255, 255), (WIDTH//2, 120))
                self.retry_btn.draw(self.screen)
                self.map_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)
                
            elif self.state == "LEVEL_TRANSITION":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                # Smooth fade out (90 to 45) and fade in (45 to 0)
                if self.transition_timer > 45:
                    alpha = min(255, (90 - self.transition_timer) * 6)
                else:
                    alpha = min(255, self.transition_timer * 6)
                
                overlay.fill((0, 0, 0, alpha))
                self.screen.blit(overlay, (0,0))
                
                # Show complete message during the first half, next level during the second
                if self.transition_timer > 45:
                    draw_text(self.screen, "LEVEL COMPLETE!", self.title_font, (0, 255, 120), (WIDTH//2, HEIGHT//2 - 20))
                else:
                    draw_text(self.screen, f"STARTING LEVEL {self.current_level_num}", self.title_font, (0, 255, 255), (WIDTH//2, HEIGHT//2 - 20))

        # Unique Developer Signature (Bottom Left)
        import math
        time_val = pygame.time.get_ticks() * 0.004
        sig_str = "MUMTAJ"
        base_x = 15
        base_y = HEIGHT - 35
        
        # Small "Created by" text
        creator_font = pygame.font.SysFont("Arial", 12, italic=True)
        c_surf = creator_font.render("Created by", True, (180, 180, 180))
        self.screen.blit(c_surf, (base_x, base_y - 15))

        # Animated Glowing Name
        for i, char in enumerate(sig_str):
            y_off = math.sin(time_val + i * 0.5) * 4  # Smooth bouncy effect
            
            # Smooth neon color shifting (Rainbow style)
            r = int(127 + 128 * math.sin(time_val + i * 0.3))
            g = int(127 + 128 * math.sin(time_val + i * 0.3 + 2))
            b = int(127 + 128 * math.sin(time_val + i * 0.3 + 4))
            
            # Black Shadow for depth
            char_surf_shadow = self.sig_font.render(char, True, (0, 0, 0))
            self.screen.blit(char_surf_shadow, (base_x + i * 18 + 2, base_y + y_off + 2))
            
            # Bright Colored Character
            char_surf = self.sig_font.render(char, True, (r, g, b))
            self.screen.blit(char_surf, (base_x + i * 18, base_y + y_off))

        pygame.display.flip()

    async def run(self):
        import asyncio
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            await asyncio.sleep(0)
        pygame.quit()
