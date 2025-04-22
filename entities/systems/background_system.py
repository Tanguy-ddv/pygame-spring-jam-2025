# Built-ins
import random
import math

# External
import pygame

class BackgroundSystem:
    def __init__(self):
        self.shooting_stars = []
    
    def spawn_new_meteor(self, camera):
        screen_border = random.randint(0, 3)
        speed = random.randint(300, 600)

        if screen_border == 0:
            direction = random.randint(225, 315)
            self.shooting_stars.append({"x":random.randint(camera.camera_x - 640, camera.camera_x + 640), "y":camera.camera_y - 360, "direction":direction, "speed":speed})
        
        elif screen_border == 1:
            direction = random.randint(45, 135)
            self.shooting_stars.append({"x":random.randint(camera.camera_x - 640, camera.camera_x + 640), "y":camera.camera_y + 360, "direction":direction, "speed":speed})
        
        elif screen_border == 2:
            direction = random.randint(-45, 45)
            self.shooting_stars.append({"x":camera.camera_x - 640, "y":random.randint(camera.camera_y - 360, camera.camera_y + 360), "direction":direction, "speed":speed})
        
        elif screen_border == 3:
            direction = random.randint(135, 225)
            self.shooting_stars.append({"x":camera.camera_x + 640, "y":random.randint(camera.camera_y - 360, camera.camera_y + 360), "direction":direction, "speed":speed})

    def cull_meteors(self, camera_bounding_box):
        # Delete off-screen meteors
        for shooting_star in self.shooting_stars.copy():
            if shooting_star["x"] < camera_bounding_box[0]:
                self.shooting_stars.remove(shooting_star)
            if shooting_star["x"] > camera_bounding_box[2]:
                self.shooting_stars.remove(shooting_star)
            if shooting_star["y"] < camera_bounding_box[1]:
                self.shooting_stars.remove(shooting_star)
            if shooting_star["y"] > camera_bounding_box[3]:
                self.shooting_stars.remove(shooting_star)

    def update(self, camera_bounding_box, delta_time):
        self.cull_meteors(camera_bounding_box)

        for shooting_star in self.shooting_stars:
            shooting_star["x"] += math.cos(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time
            shooting_star["y"] += math.sin(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time

    def draw(self, surface, camera, Images):
        for shooting_star in self.shooting_stars:
            position = camera.get_relative_position((shooting_star["x"], shooting_star["y"]))
            image = Images.get_image("shooting_star variant " + "0").copy()
            image = pygame.transform.rotate(image, -shooting_star["direction"])
            surface.blit(image, image.get_rect(center = position))