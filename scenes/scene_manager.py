# External
import pygame

# Internal
from utils import Singleton

# Scene class
class Scene:
    def __init__(self):
        pass

    def update(self, delta_time: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass

# Scene manager class
class SceneManager(Singleton):
    def __init__(self):
        self.scenes = {}
        self.active_scene = ""

    def update(self, delta_time: float) -> None:
        if self.active_scene not in self.scenes.keys():
            return

    def draw(self, surface: pygame.Surface) -> None:
        if self.active_scene not in self.scenes.keys():
            return
        
        self.scenes[self.active_scene].draw(surface)