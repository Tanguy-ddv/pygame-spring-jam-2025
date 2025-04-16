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
        self.image_dict = {}

    def load_json(self, path_to_json: PathLike) -> None:
        with open(path_to_json, "r") as json_file:
            images = json.load(json_file)

        for path_to_image, name in images.items():
            self.load_image(path_to_image, name)

    def load_image(self, path_to_image: FileLike, name: str) -> pygame.Surface:
        image = pygame.image.load(path_to_image)
        self.register_image(image, name)

        return image

    def register_image(self, image: pygame.Surface, name: str) -> None:
        self.image_dict[name] = image

    def get_image(self, name: str) -> pygame.Surface:
        pass