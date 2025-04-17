# Built-ins
import json
from os import PathLike

# External
import pygame

# Internal
from pygamelib.utils import Singleton

class SoundManager(Singleton):
    def __init__(self):
        self.sound_dict: dict[str, pygame.mixer.Sound] = {}

    def load_json(self, path_to_json: PathLike) -> None:
        with open(path_to_json, "r") as json_file:
            sounds = json.load(json_file)

        for path_to_sound, sound_name in sounds.items():
            self.load_sound(path_to_sound, sound_name)

    def load_sound(self, path_to_sound: PathLike, sound_name: str) -> pygame.mixer.Sound:
        sound = pygame.Sound(path_to_sound)
        self.register_sound(sound, sound_name)

        return sound

    def register_sound(self, sound: pygame.mixer.Sound, sound_name: str) -> None:
        self.sound_dict[sound_name] = sound

    def get_sound(self, sound_name: str) -> pygame.mixer.Sound:
        return self.sound_dict[sound_name]