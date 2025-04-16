# Built-ins
import json

# External
import pygame
from pygame.typing import _PathLike

# Internal
from utils import Singleton

class SoundManager(Singleton):
    def __init__(self):
        self.sounds = dict()

    def load_json(self, path_to_json: _PathLike) -> None:
        pass

    def load_sound(self, path_to_sound: _PathLike, name: str) -> None:
        pass

    def add_sound(self, sound: pygame.Sound, name: str) -> None:
        pass

    def get_sound(self, name: str) -> pygame.Sound:
        pass