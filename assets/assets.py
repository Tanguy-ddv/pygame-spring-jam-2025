import pygame
from pygame.locals import *
from pygamelib import *
from assets.image_caching import *

pygame.init()
temp_screen = pygame.display.set_mode((50, 50))

# Sound init
Sounds = SoundManager()
Sounds.load_json("assets/jsons/sounds.json")

# Font init
Fonts = FontManager()
Fonts.register_font(pygame.font.SysFont("Verdana", 32), "Verdana")

# Image init
Images = ImageManager()
Images.load_json("assets/jsons/images.json")
cache_size_variants(Images.get_image("star"), "star", Images, 50)
cache_size_variants(Images.get_image("shooting_star"), "shooting_star", Images, 25)

# Text pre-rendering
Images.register_image(Fonts.get_font("Verdana").render("[PRESS ANY KEY TO START]", True, (60, 60, 60)), "start prompt")

# Animation init
Animations = AnimationManager()
Animations.load_json("assets/jsons/animations.json")