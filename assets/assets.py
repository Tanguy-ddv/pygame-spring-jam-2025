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
Images.register_image(Fonts.get_font("Body").render("[PRESS ANY KEY TO RESTART]", True, (255, 255, 255)), "restart prompt")
Images.register_image(Fonts.get_font("Body").render("[PRESS ESCAPE TO UNPAUSE]", True, (255, 255, 255)), "unpause prompt")
Images.register_image(Fonts.get_font("Title").render("PAUSED" , True, (180, 180, 180)), "pause text")
Images.register_image(Fonts.get_font("Title").render("GAMEOVER" , True, (180, 180, 180)), "gameover text")
Images.register_image(Fonts.get_font("Title").render("ISC-PIONEER", True, (180, 180, 180)), "title text")
Images.register_image(Fonts.get_font("Body").render("MISSIONS", True, (255, 255, 255)), "log text")

image = pygame.Surface((400, 268))
image.fill((50, 50, 50))

y = 10
image.blit(Fonts.get_font("Tiny").render("W to engage the main drive", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("A or D to rotate", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("SPACE to shoot", True, (255, 255, 255)), (10, y)); y += 16; y += 8
image.blit(Fonts.get_font("Tiny").render("M to show the map", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("V to change map view", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("TAB to change map mode", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("J to toggle mission board", True, (255, 255, 255)), (10, y)); y += 16; y += 8
image.blit(Fonts.get_font("Tiny").render("CLICK on planets to access their trade", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("information", True, (255, 255, 255)), (10, y)); y += 16; y += 8
image.blit(Fonts.get_font("Tiny").render("T to toggle this menu", True, (255, 255, 255)), (10, y)); y += 16; y += 8
image.blit(Fonts.get_font("Tiny").render("ESC to pause", True, (255, 255, 255)), (10, y)); y += 16; y += 8
image.blit(Fonts.get_font("Tiny").render("Complete missions to earn cash, ", True, (255, 255, 255)), (10, y)); y += 16
image.blit(Fonts.get_font("Tiny").render("more cash = higher score", True, (255, 255, 255)), (10, y)); y += 16

Images.register_image(image, "manual")

# Prerender planet names
with open("data/celestial_bodies.json", "r") as file:
    names = json.load(file).keys()

for planet_name in names:
    Images.register_image(Fonts.get_font("Body").render(planet_name.capitalize(), True, (255, 255, 255)), planet_name + " title")

# Animation init
Animations = AnimationManager()
Animations.load_json("assets/jsons/animations.json")