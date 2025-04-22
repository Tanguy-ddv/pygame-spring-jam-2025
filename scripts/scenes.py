import pygame
import random
import math
from pygamelib import *
from scripts.assets.assets import Images

#real camera position -> camera position without rounding
#camera position -> camera position with rounding
class Camera:
    def __init__(self, screen_size:tuple, starting_position:tuple):
        self.screen_size = screen_size
        self.relative_offset = (screen_size[0] / 2, screen_size[1] / 2)
        self.real_camera_x, self.real_camera_y = starting_position

    @property
    def camera_x(self):
        return round(self.real_camera_x)
    
    @property
    def camera_y(self):
        return round(self.real_camera_y)

    def get_relative_position(self, position:tuple):
        return (position[0] - self.camera_x + self.relative_offset[0], position[1] - self.camera_y + self.relative_offset[1])
    
    def get_bounding_box(self, padding:int):
        return (self.camera_x - self.relative_offset[0] - padding, self.camera_y - self.relative_offset[1] - padding, 
                self.camera_x + self.relative_offset[0] + padding, self.camera_y + self.relative_offset[1] + padding)

class Space(scene.Scene):
    def __init__(self):
        #camera
        self.camera = Camera((1280, 720), (640, 360))

        #background stars
        self.stars = []
        self.shooting_stars = []

        for i in range(100):
            self.stars.append({"x":random.randint(0, 1280), "y":random.randint(0, 720), "star_type":str(random.randint(0, 49))})


    def start(self) -> None:
        pass

    def handle_events(self, events:list[pygame.Event]) -> None:
        pass

    def update(self, delta_time:float) -> None:
        self.camera.real_camera_x += 300 * delta_time

        #updating stars
        camera_bounding_box = self.camera.get_bounding_box(50)
        for star in self.stars:
            if star["x"] < camera_bounding_box[0]:
                star["x"] = camera_bounding_box[2]
                star["y"] = random.randint(self.camera.camera_y - 360, self.camera.camera_y + 360)
            if star["x"] > camera_bounding_box[2]:
                star["x"] = camera_bounding_box[0]
                star["y"] = random.randint(self.camera.camera_y - 360, self.camera.camera_y + 360)
            if star["y"] < camera_bounding_box[1]:
                star["y"] = camera_bounding_box[3]
                star["x"] = random.randint(self.camera.camera_x - 640, self.camera.camera_y + 640)
            if star["y"] > camera_bounding_box[3]:
                star["y"] = camera_bounding_box[1]
                star["x"] = random.randint(self.camera.camera_x - 640, self.camera.camera_y + 640)

        #updating meteors:
        for shooting_star in self.shooting_stars:
            shooting_star["x"] += math.cos(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time
            shooting_star["y"] += math.sin(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time

        #deleting offscreen meteors
        for shooting_star in self.shooting_stars.copy():
            if shooting_star["x"] < camera_bounding_box[0]:
                self.shooting_stars.remove(shooting_star)
            if shooting_star["x"] > camera_bounding_box[2]:
                self.shooting_stars.remove(shooting_star)
            if shooting_star["y"] < camera_bounding_box[1]:
                self.shooting_stars.remove(shooting_star)
            if shooting_star["y"] > camera_bounding_box[3]:
                self.shooting_stars.remove(shooting_star)

        #spawning new meteors
        if random.randint(0, 300) == 0:
            screen_border = random.randint(0, 3)
            speed = random.randint(300, 600)
            if screen_border == 0:
                direction = random.randint(225, 315)
                self.shooting_stars.append({"x":random.randint(self.camera.camera_x - 640, self.camera.camera_x + 640), "y":self.camera.camera_y - 360, "direction":direction, "speed":speed})
            elif screen_border == 1:
                direction = random.randint(45, 135)
                self.shooting_stars.append({"x":random.randint(self.camera.camera_x - 640, self.camera.camera_x + 640), "y":self.camera.camera_y + 360, "direction":direction, "speed":speed})
            elif screen_border == 2:
                direction = random.randint(-45, 45)
                self.shooting_stars.append({"x":self.camera.camera_x - 640, "y":random.randint(self.camera.camera_y - 360, self.camera.camera_y + 360), "direction":direction, "speed":speed})
            elif screen_border == 3:
                direction = random.randint(135, 225)
                self.shooting_stars.append({"x":self.camera.camera_x + 640, "y":random.randint(self.camera.camera_y - 360, self.camera.camera_y + 360), "direction":direction, "speed":speed})

    def draw(self, surface:pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        
        for star in self.stars:
            position = self.camera.get_relative_position((star["x"], star["y"]))
            image = Images.get_image("star variant " + star["star_type"])
            surface.blit(image, image.get_rect(center = position))

        for shooting_star in self.shooting_stars:
            position = self.camera.get_relative_position((shooting_star["x"], shooting_star["y"]))
            image = Images.get_image("shooting_star variant " + "0").copy()
            image = pygame.transform.rotate(image, -shooting_star["direction"])
            surface.blit(image, image.get_rect(center = position))

    def stop(self) -> None:
        pass