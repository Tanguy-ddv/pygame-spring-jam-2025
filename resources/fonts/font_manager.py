# Built-ins
import json
from os import PathLike

# External
import pygame
from pygame.typing import FileLike

# Internal
from utils import Singleton

# Font class
class Font:
    def __init__(self, font: pygame.font.Font):
        pass

# FontLike type
FontLike = pygame.font.Font | Font

# Font manager class
class FontManager(Singleton):
    def __init__(self):
        self.font_dict = {}

    def load_json(self, path_to_json: PathLike) -> None:
        with open(path_to_json, "r") as json_file:
            fonts = json.load(json_file)

        for path_to_font, name in fonts.items():
            self.load_font(path_to_font, name)

    def load_font(self, filename: FileLike, size: int, name: str) -> Font:
        font = Font(pygame.font.Font(filename, size))
        self.register_font(font)

        return font
    
    def register_font(self, font: FontLike, name: str) -> None:
        self.font_dict[name] = font

    def get_font(self, name: str) -> FontLike:
        return self.font_dict[name]