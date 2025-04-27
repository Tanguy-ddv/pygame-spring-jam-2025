# Built-ins
import random
import math

# External
import pygame

from . import camera_system
from pygamelib import *

class BackgroundSystem:
    def __init__(self):
        self.stars = []
        for i in range(100):
            self.stars.append({"x":random.randint(0, 1280), "y":random.randint(0, 720), "star_type":str(random.randint(0, 49))})
        
        self.shooting_stars = []
    
    def reset_stars(self, camera):
        self.stars = []
        for i in range(100):
            self.stars.append({"x":random.randint(0, camera.internal_surface.size[0]), "y":random.randint(0, camera.internal_surface.size[1]), "star_type":str(random.randint(0, 49))})
        
    def spawn_new_meteor(self, camera:camera_system.CameraSystem):
        screen_border = random.randint(0, 3)
        speed = random.randint(450, 600)

        if screen_border == 0:
            direction = random.randint(45, 135)
            self.shooting_stars.append({"x":random.randint(int(camera.camera_x - camera.internal_surface.size[0] / 2), int(camera.camera_x + camera.internal_surface.size[0] / 2)), "y":camera.camera_y - camera.internal_surface.size[1] / 2, "direction":direction, "speed":speed, "star_type":str(random.randint(0, 24))})
        
        elif screen_border == 1:
            direction = random.randint(225, 315)
            self.shooting_stars.append({"x":random.randint(int(camera.camera_x - camera.internal_surface.size[0] / 2), int(camera.camera_x + camera.internal_surface.size[0] / 2)), "y":camera.camera_y + camera.internal_surface.size[1] / 2, "direction":direction, "speed":speed, "star_type":str(random.randint(0, 24))})
        
        elif screen_border == 2:
            direction = random.randint(-45, 45)
            self.shooting_stars.append({"x":camera.camera_x - camera.internal_surface.size[0] / 2, "y":random.randint(int(camera.camera_y - camera.internal_surface.size[1] / 2), int(camera.camera_y + camera.internal_surface.size[1] / 2)), "direction":direction, "speed":speed, "star_type":str(random.randint(0, 24))})
        
        elif screen_border == 3:
            direction = random.randint(135, 225)
            self.shooting_stars.append({"x":int(camera.camera_x + camera.internal_surface.size[0] / 2), "y":random.randint(int(camera.camera_y - camera.internal_surface.size[1] / 2), int(camera.camera_y + camera.internal_surface.size[1] / 2)), "direction":direction, "speed":speed, "star_type":str(random.randint(0, 24))})

    def cull_meteors(self, camera_bounding_box:tuple):
        # Delete off-screen meteors
        for shooting_star in self.shooting_stars.copy():
            if shooting_star["x"] < camera_bounding_box[0]:
                self.shooting_stars.remove(shooting_star)
            elif shooting_star["x"] > camera_bounding_box[2]:
                self.shooting_stars.remove(shooting_star)
            elif shooting_star["y"] < camera_bounding_box[1]:
                self.shooting_stars.remove(shooting_star)
            elif shooting_star["y"] > camera_bounding_box[3]:
                self.shooting_stars.remove(shooting_star)

    def update(self, camera:camera_system.CameraSystem, delta_time:float):
        camera_bounding_box = camera.get_bounding_box(50)
        self.cull_meteors(camera_bounding_box)

        self.update_stars(camera, camera_bounding_box, delta_time)
        self.update_meteors(delta_time)

        # Spawn new meteor
        if random.randint(0, 300) == 0:
            self.spawn_new_meteor(camera)

    def update_meteors(self, delta_time:float):
        for shooting_star in self.shooting_stars:
            shooting_star["x"] += math.cos(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time
            shooting_star["y"] += math.sin(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time

    def update_stars(self, camera:camera_system.CameraSystem, camera_bounding_box:tuple, delta_time:float):
        for star in self.stars:
            if star["x"] < camera_bounding_box[0]:
                star["x"] = camera_bounding_box[2] + (star["x"] - camera_bounding_box[0])
                star["y"] = random.randint(int(camera.camera_y - camera.internal_surface.size[1] / 2), int(camera.camera_y + camera.internal_surface.size[1] / 2))

            elif star["x"] > camera_bounding_box[2]:
                star["x"] = camera_bounding_box[0] + (star["x"] - camera_bounding_box[2])
                star["y"] = random.randint(int(camera.camera_y - camera.internal_surface.size[1] / 2), int(camera.camera_y + camera.internal_surface.size[1] / 2))

            if star["y"] < camera_bounding_box[1]:
                star["y"] = camera_bounding_box[3] + (star["y"] - camera_bounding_box[1])
                star["x"] = random.randint(int(camera.camera_x - camera.internal_surface.size[0] / 2), int(camera.camera_x + camera.internal_surface.size[0] / 2))

            elif star["y"] > camera_bounding_box[3]:
                star["y"] = camera_bounding_box[1] + (star["y"] - camera_bounding_box[3])
                star["x"] = random.randint(int(camera.camera_x - camera.internal_surface.size[0] / 2), int(camera.camera_x + camera.internal_surface.size[0] / 2))

    def draw(self, surface:pygame.Surface, camera:camera_system.CameraSystem, Images:images.ImageManager):
        self.draw_stars(surface, camera, Images)
        self.draw_meteors(surface, camera, Images)

    def draw_stars(self, surface:pygame.Surface, camera:camera_system.CameraSystem, Images:images.ImageManager):
        for star in self.stars:
            position = camera.get_relative_position((star["x"], star["y"]))
            image = Images.get_image("star variant " + star["star_type"])
            surface.blit(image, image.get_rect(center = position), special_flags=pygame.BLEND_RGB_ADD)

    def draw_meteors(self, surface:pygame.Surface, camera:camera_system.CameraSystem, Images:images.ImageManager):
        for shooting_star in self.shooting_stars:
            position = camera.get_relative_position((shooting_star["x"], shooting_star["y"]))
            image = Images.get_image("shooting_star variant " + shooting_star["star_type"]).copy()
            image = pygame.transform.rotate(image, -shooting_star["direction"])
            surface.blit(image, image.get_rect(center = position), special_flags=pygame.BLEND_RGB_ADD)
