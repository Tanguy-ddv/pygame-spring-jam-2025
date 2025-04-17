# External
import pygame

# Internal
from pygamelib.utils import Singleton

# Scene class
class Scene:
    def start(self) -> None:
        pass

    def handle_events(self, events: list[pygame.Event]) -> None:
        pass

    def update(self, delta_time: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def stop(self) -> None:
        pass

# Scene manager class
class SceneManager(Singleton):
    def __init__(self):
        self.scene_dict: dict[str, Scene] = {}
        self.current_scene: str = ""

    def register_scene(self, scene: type[Scene], scene_name: str) -> None:
        self.scene_dict[scene_name] = scene

    def unregister_scene(self, scene_name: str) -> None:
        self.scene_dict.pop(scene_name)

    def set_scene(self, scene_name: str) -> None:
        if scene_name not in self.scene_dict.keys():
            return
        
        self.scene_dict[self.current_scene].stop()
        self.scene_dict[scene_name].start()

        self.current_scene = scene_name

    def handle_events(self, events: list[pygame.Event]) -> None:
        if self.current_scene not in self.scene_dict.keys():
            return
        
        self.scene_dict[self.current_scene].handle_events(events)

    def update(self, delta_time: float) -> None:
        if self.current_scene not in self.scene_dict.keys():
            return
        
        self.scene_dict[self.current_scene].update(delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        if self.current_scene not in self.scene_dict.keys():
            return
        
        self.scene_dict[self.current_scene].draw(surface)