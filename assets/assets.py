import pygame
from pygame.locals import *
from pygamelib import *
from assets.image_caching import *

pygame.init()
temp_screen = pygame.display.set_mode((50, 50))

# Image init
Images = ImageManager()
Images.load_json("assets/jsons/images.json")
cache_size_variants(Images.get_image("star"), "star", Images, 50)
cache_size_variants(Images.get_image("shooting_star"), "shooting_star", Images, 25)

# Animation init
Animations = AnimationManager()
Animations.load_json("assets/jsons/animations.json")

# TEMP VVVVVVVVv

# Player image
player_image = pygame.Surface((50, 50), SRCALPHA)
pygame.draw.polygon(player_image, (255, 0, 0), [(0, 0), (0, 50), (50, 25)])

Images.register_image(player_image, "player")