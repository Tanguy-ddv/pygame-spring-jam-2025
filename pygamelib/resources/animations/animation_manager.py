# Built-ins
import json
import math
from os import PathLike, listdir
from copy import deepcopy

# External
import pygame

# Internal
from ...utils import Singleton

"""

DOCUMENTATION:

to use a json:

resources folder:
 - json
 - animation folders

animation folder should contain a series of images, i.e. frame 0, frame 1, frame 2, and so forth

structure the json as follows:
{
    path to folder: {"name": string, "duration": integer}
}

"""

class AnimationManager(Singleton):
    def __init__(self):
        self.animation_dict: dict[str, dict] = {}

    def load_json(self, path_to_json: PathLike, colorkey: tuple = (0, 0, 0)) -> None:
        with open(path_to_json, "r") as json_file:
            animations = json.load(json_file)

        for animation_folder, animation_data in animations.items():
            self.load_animation(animation_folder, animation_data["name"], animation_data["duration"], colorkey)

    def load_animation(self, animation_folder: PathLike, animation_name: str, duration: int, colorkey: tuple = (0, 0, 0)) -> pygame.surface.Surface:
        images_in_folder = listdir(animation_folder)

        images_in_folder.sort()

        images = [pygame.image.load(animation_folder + "/" + path_to_image).convert() for path_to_image in images_in_folder]
        self.register_animation(images, animation_name, duration, colorkey)

        return images
    
    def register_animation(self, images: list[pygame.surface.Surface], animation_name: str, duration: int, colorkey: tuple = (0, 0, 0)):
        for image in images:
            image.set_colorkey(colorkey)

        self.animation_dict[animation_name] = {"data":(duration, math.floor(duration / len(images))), "images":images.copy()}

    def get_animation(self, animation_name: str, frame: int) -> pygame.surface.Surface:
        animation_data = self.animation_dict[animation_name]["data"]
        return self.animation_dict[animation_name]["images"][math.floor((frame % animation_data[0]) / animation_data[1])].copy()