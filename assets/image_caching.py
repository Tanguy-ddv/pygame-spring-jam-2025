import pygame
import random
from pygamelib import *

def cache_size_variants(original_surface:pygame.surface.Surface, image_name:str, image_handler:image_manager.ImageManager, variations:int):
    for i in range(variations):
        size = random.randint(50, 200)/100
        surface = pygame.transform.scale(original_surface.copy(), (original_surface.get_width() * size, original_surface.get_height() * size))
        image_handler.register_image(surface, image_name + " variant " + str(i))