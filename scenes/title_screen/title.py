# Built-ins
import math

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib import *
from assets import *

class Title(Scene):
    def __init__(self):
        # Scene manager
        self.scene_manager = SceneManager()

        # Variables
        self.transition_timer = None
        self.prompt_colour = [0, 0, 0]
        self.time_elapsed = 0

    def start(self):
        return super().start()
    
    def handle_events(self, events):
        for event in events:
            if event.type in [KEYDOWN, MOUSEBUTTONDOWN]:
                Sounds.get_sound("select").play()
                self.transition_timer = Sounds.get_sound("select").get_length()

    
    def update(self, delta_time):
        self.time_elapsed += delta_time

        if self.transition_timer != None:
            if self.transition_timer <= 0:
                self.scene_manager.set_scene("space")

            else:
                self.transition_timer -= delta_time
                for i, _ in enumerate(self.prompt_colour):
                    self.prompt_colour[i] = abs(math.sin(math.radians(self.time_elapsed * 800))) * 90

        else:
            for i, _ in enumerate(self.prompt_colour):
                self.prompt_colour[i] = abs(math.sin(math.radians(self.time_elapsed * 40))) * 60 + 100
        
    def draw(self, surface):
        prompt_image = Images.get_image("start prompt").copy()
        prompt_image.fill(self.prompt_colour, special_flags=BLEND_RGB_SUB)

        title_image = Images.get_image("title text")

        surface.blit(prompt_image, (1280 / 2 - prompt_image.get_width() / 2, 600))
        surface.blit(title_image, (1280 / 2 - title_image.get_width() / 2, 50))
    
    def stop(self):
        return super().stop()