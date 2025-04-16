# Built-ins
import json
from os import PathLike

# External
import pygame
from pygame.typing import FileLike

# Internal
from utils import Singleton

class SoundManager(Singleton):
    def __init__(self):
        self.sound_dict = {}

    def load_json(self, path_to_json: PathLike) -> None:
        with open(path_to_json, "r") as json_file:
            sounds = json.load(json_file)

        for path_to_sound, name in sounds.items():
            self.load_sound(path_to_sound, name)

    def load_sound(self, path_to_sound: FileLike, name: str) -> pygame.Sound:
        sound = pygame.Sound(path_to_sound)
        self.register_sound(sound, name)

        return sound

    def register_sound(self, sound: pygame.Sound, name: str) -> None:
        self.sound_dict[name] = sound

    def get_sound(self, name: str) -> pygame.Sound:
        pass