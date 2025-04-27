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

    def start(self):
        return super().start()
    
    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN:
                self.scene_manager.set_scene("space")
    
    def update(self, delta_time):
        return super().update(delta_time)
    
    def draw(self, surface):
        surface.blit(Images.get_image("start prompt"), (500, 500))
        return super().draw(surface)
    
    def stop(self):
        return super().stop()