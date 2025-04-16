# Built-ins
import json

# External
import pygame
from pygame.typing import _PathLike

# Internal
from utils import Singleton

class ImageManager(Singleton):
    def __init__(self):
        self.images = dict()

    def load_json(self, path_to_json: _PathLike) -> None:
        pass

    def load_image(self, path_to_image: _PathLike, name: str) -> None:
        pass

    def add_image(self, image: pygame.Surface, name: str) -> None:
        pass

    def get_image(self, name) -> pygame.Surface:
        pass