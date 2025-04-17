# Built-ins
import json
from os import PathLike

# External
import pygame
from pygame.typing import FileLike

# Internal
from utils import Singleton

class ImageManager(Singleton):
    def __init__(self):
        self.image_dict: dict[str, pygame.Surface] = {}

    def load_json(self, path_to_json: PathLike) -> None:
        with open(path_to_json, "r") as json_file:
            images = json.load(json_file)

        for path_to_image, image_name in images.items():
            self.load_image(path_to_image, image_name)

    def load_image(self, path_to_image: FileLike, image_name: str) -> pygame.Surface:
        image = pygame.image.load(path_to_image)
        self.register_image(image, image_name)

        return image

    def register_image(self, image: pygame.Surface, image_name: str) -> None:
        self.image_dict[image_name] = image

    def get_image(self, image_name: str) -> pygame.Surface:
        return self.image_dict[image_name]