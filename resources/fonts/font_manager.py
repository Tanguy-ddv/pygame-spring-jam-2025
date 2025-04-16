# Built-ins
import json

# External
import pygame
from pygame.typing import _PathLike

# Internal
from utils import Singleton

class FontManager(Singleton):
    def __init__(self):
        self.fonts = dict()

    def load_json(self, path_to_json: _PathLike) -> None:
        pass

    def load_font(self, path_to_font: _PathLike, name: str) -> None:
        pass
    
    def add_font(self, font: _PathLike, name: str) -> None:
        pass

    def get_font(self, name: str):
        pass