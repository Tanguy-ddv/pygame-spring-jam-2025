# Built-ins
from __future__ import annotations

# External
import pygame

# Internal
from .scene import Scene
from ..utils import Singleton

# Scene Manager class
class SceneManager(Singleton):
    def __init__(self):
        self.scene_dict: dict[str, type[Scene]] = {}
        self.current_scene: str = ""

    def register_scene(self, scene: type[Scene], scene_name: str) -> None:
        self.scene_dict[scene_name] = scene

    def unregister_scene(self, scene_name: str) -> None:
        self.scene_dict.pop(scene_name)

    def set_scene(self, scene_name: str) -> None:
        if scene_name not in self.scene_dict:
            return
        
        if self.current_scene in self.scene_dict:
            self.scene_dict[self.current_scene].stop()

        self.scene_dict[scene_name].start()
        self.current_scene = scene_name

    def handle_events(self, events: list[pygame.Event], delta_time: float) -> None:
        if self.current_scene not in self.scene_dict:
            return
        
        self.scene_dict[self.current_scene].handle_events(events, delta_time)

    def update(self, delta_time: float) -> None:
        if self.current_scene not in self.scene_dict:
            return
        
        self.scene_dict[self.current_scene].update(delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        if self.current_scene not in self.scene_dict:
            return
        
        self.scene_dict[self.current_scene].draw(surface)
