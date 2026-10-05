import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        
        self.is_hovered = False
        self.current_color = list(bg_color)
        self.animation_speed = 0.15

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = self.hover_color if self.is_hovered else self.bg_color
        
        # Smooth color transition
        self.current_color[0] += (target[0] - self.current_color[0]) * self.animation_speed
        self.current_color[1] += (target[1] - self.current_color[1]) * self.animation_speed
        self.current_color[2] += (target[2] - self.current_color[2]) * self.animation_speed

    def draw(self, surface):
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (15, 15, 15), shadow_rect, border_radius=8)
        
        # Draw main button body
        pygame.draw.rect(surface, (int(self.current_color[0]), int(self.current_color[1]), int(self.current_color[2])), self.rect, border_radius=8)
        
        # Draw border on hover
        if self.is_hovered:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, width=2, border_radius=8)
            
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        # Slight text shift on hover
        if self.is_hovered:
            text_rect.y -= 1
            
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

def draw_text(surface, text, font, color, center_pos):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, text_rect)

class LevelNodeButton(Button):
    def __init__(self, x, y, radius, level_num, status, font):
        # status: "COMPLETED", "CURRENT", "LOCKED"
        super().__init__(x - radius, y - radius, radius*2, radius*2, str(level_num), font, (100,100,100), (150,150,150))
        self.radius = radius
        self.level_num = level_num
        self.status = status
        
        if status == "COMPLETED":
            self.bg_color = (46, 204, 113) # Green
            self.hover_color = (39, 174, 96)
        elif status == "CURRENT":
            self.bg_color = (52, 152, 219) # Blue
            self.hover_color = (41, 128, 185)
        else: # LOCKED
            self.bg_color = (80, 80, 80)
            self.hover_color = (80, 80, 80)
            
        self.current_color = list(self.bg_color)
        
    def draw(self, surface):
        # Overwrite draw to draw a circle
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.circle(surface, (15, 15, 15), (self.rect.centerx, self.rect.centery + 4), self.radius)
        
        pygame.draw.circle(surface, (int(self.current_color[0]), int(self.current_color[1]), int(self.current_color[2])), self.rect.center, self.radius)
        
        if self.is_hovered and self.status != "LOCKED":
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, self.radius, width=2)
            
        # Text/Icons
        if self.status == "LOCKED":
            # Simple lock icon (using text 'L' or a lock symbol)
            text_surf = self.font.render("X", True, (150, 150, 150))
        else:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            
        text_rect = text_surf.get_rect(center=self.rect.center)
        if self.is_hovered and self.status != "LOCKED":
            text_rect.y -= 2
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.status != "LOCKED":
                return True
        return False

