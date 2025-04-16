# Internal
from utils import Singleton

class SceneManager(Singleton):
    def __init__(self):
        self.scenes = dict()
        self.active_scene = ""

    def update(self, delta_time):
        if self.active_scene not in self.scenes.keys():
            return

    def draw(self, surface):
        if self.active_scene not in self.scenes.keys():
            return
        
        self.scenes[self.active_scene].draw(surface)