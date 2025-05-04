# Built-ins
import json
from os import PathLike

# External
import pygame

# Internal
from ...utils import Singleton

class ImageManager(Singleton):
    def __init__(self):
        self.image_dict: dict[str, pygame.surface.Surface] = {}

    def load_json(self, path_to_json: PathLike, colorkey: tuple = (0, 0, 0)) -> None:
        with open(path_to_json, "r") as json_file:
            images = json.load(json_file)

        for path_to_image, image_name in images.items():
            self.load_image(path_to_image, image_name, colorkey)

    def load_image(self, path_to_image: PathLike, image_name: str, colorkey: tuple = (0, 0, 0)) -> pygame.surface.Surface:
        image = pygame.image.load(path_to_image).convert()
        self.register_image(image, image_name, colorkey)

        return image

    def register_image(self, image: pygame.surface.Surface, image_name: str, colorkey: tuple = (0, 0, 0)) -> None:
        image.set_colorkey(colorkey)
        self.image_dict[image_name] = image

    def get_image(self, image_name: str) -> pygame.surface.Surface:
        return self.image_dict[image_name].copy()