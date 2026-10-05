import os
import pygame

class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.base_dir = os.path.join(os.path.dirname(__file__), "assets", "sounds")
        self.sounds = {}
        
        # Configuration
        self.sound_enabled = True
        self.music_enabled = True
        
        # Default sounds mapping
        self.load_sound("eat", ["eat.wav", "freesound_community-eating-sound-effect-36186.mp3"])
        self.load_sound("gameover", ["gameover.wav", "viralaudio-descent-whoosh-long-cinematic-sound-effect-405921.mp3"])
        self.load_sound("coin", ["coin.wav", "freesound_community-eating-sound-effect-36186.mp3"]) # fallback
        self.bg_music_loaded = self.load_music(["background.mp3", "alexzavesa-drums-action-the-end-5-459019.mp3"])
        
    def apply_settings(self, sound_on, music_on):
        self.sound_enabled = sound_on
        self.music_enabled = music_on
        
        if not self.music_enabled:
            pygame.mixer.music.stop()
        elif self.bg_music_loaded and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    def load_sound(self, name, fallback_candidates):
        for candidate in fallback_candidates:
            path = os.path.join(self.base_dir, candidate)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    return True
                except pygame.error:
                    continue
        return False

    def load_music(self, fallback_candidates):
        for candidate in fallback_candidates:
            path = os.path.join(self.base_dir, candidate)
            if os.path.exists(path):
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(0.4)
                    return True
                except pygame.error:
                    continue
        return False

    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()
            
    def play_music(self):
        if self.music_enabled and self.bg_music_loaded:
            pygame.mixer.music.play(-1)

