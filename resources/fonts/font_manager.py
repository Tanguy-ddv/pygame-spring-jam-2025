# Built-ins
import json
from os import PathLike

# External
import pygame

# Internal
from utils import Singleton

# Font class
class Font:
    def __init__(self):
        print("NOT IMPLEMENTED CUSTOM FONT USE 'pygame.font.Font' instead") # I plan on making my own custom font class for performance (WIP)

# FontLike type
FontLike = pygame.font.Font | Font

# Font manager class
class FontManager(Singleton):
    def __init__(self):
        self.font_dict: dict[str, FontLike] = {}

    def load_json(self, path_to_json: PathLike) -> None:
        with open(path_to_json, "r") as json_file:
            fonts = json.load(json_file)

        for path_to_font, font_name in fonts.items():
            self.load_font(path_to_font, font_name)

    def load_font(self, filename: PathLike, size: int, font_name: str) -> pygame.font.Font:
        font = pygame.font.Font(filename, size)
        self.register_font(font, font_name)

        return font
    
    def register_font(self, font: FontLike, font_name: str) -> None:
        self.font_dict[font_name] = font

    def get_font(self, font_name: str) -> FontLike:
        return self.font_dict[font_name]