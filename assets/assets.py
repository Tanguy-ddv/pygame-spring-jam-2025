import pygame
import json
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
Fonts.load_json("assets/jsons/fonts.json")

# Image init
Images = ImageManager()
Images.load_json("assets/jsons/images.json")
cache_size_variants(Images.get_image("star"), "star", Images, 50)
cache_size_variants(Images.get_image("shooting_star"), "shooting_star", Images, 25)

# Text pre-rendering
Images.register_image(Fonts.get_font("Body").render("[PRESS ANY KEY TO START]", True, (255, 255, 255)), "start prompt")
Images.register_image(Fonts.get_font("Title").render("ISC-PIONEER", True, (180, 180, 180)), "title text")

# Prerender planet names
with open("data/celestial_bodies.json", "r") as file:
    names = json.load(file).keys()

for planet_name in names:
    Images.register_image(Fonts.get_font("Body").render(planet_name.capitalize(), True, (255, 255, 255)), planet_name + " title")

# Pirate rendering
image = pygame.Surface((50, 50))
pygame.draw.polygon(image, (0, 255, 0), [(0, 0), (50, 25), (0, 50)])
Images.register_image(image, "pirate")

# Animation init
Animations = AnimationManager()
Animations.load_json("assets/jsons/animations.json")