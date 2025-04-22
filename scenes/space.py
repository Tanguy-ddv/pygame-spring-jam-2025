# Built-ins
import random
import math

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *
from assets import Images

class Space(scene.Scene):
    def __init__(self):
        # Entity manager
        self.entity_manager = EntityManager()

        # Systems
        self.input_system = InputSystem()
        self.event_system = EventSystem()
        self.physics_system = PhysicsSystem()

        self.camera = CameraSystem((1280, 720), (640, 360))

        # Player
        self.player_id = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.player_id, Listener({
            KEYDOWN: [self.input_system],
            KEYUP: [self.input_system]
        }))

        self.entity_manager.add_component(self.player_id, Position(640, 360))
        self.entity_manager.add_component(self.player_id, Velocity(0, 0))
        self.entity_manager.add_component(self.player_id, Force(0, 0))
        self.entity_manager.add_component(self.player_id, Mass(1))

        # Background stars
        self.stars = []
        self.shooting_stars = []

        for i in range(100):
            self.stars.append({"x":random.randint(0, 1280), "y":random.randint(0, 720), "star_type":str(random.randint(0, 49))})

    def start(self) -> None:
        pass

    def handle_events(self, events: list[pygame.Event]) -> None:
        self.event_system.handle_events(self.entity_manager, events)

    def update(self, delta_time: float) -> None:
        self.input_system.update()
        self.physics_system.update(self.entity_manager, delta_time)
        self.camera.set_position(self.entity_manager.get_component(self.player_id, Position))

        # Update stars
        camera_bounding_box = self.camera.get_bounding_box(50)
        for star in self.stars:
            if star["x"] < camera_bounding_box[0]:
                star["x"] = camera_bounding_box[2]
                star["y"] = random.randint(self.camera.camera_y - 360, self.camera.camera_y + 360)
            elif star["x"] > camera_bounding_box[2]:
                star["x"] = camera_bounding_box[0]
                star["y"] = random.randint(self.camera.camera_y - 360, self.camera.camera_y + 360)

            if star["y"] < camera_bounding_box[1]:
                star["y"] = camera_bounding_box[3]
                star["x"] = random.randint(self.camera.camera_x - 640, self.camera.camera_y + 640)

            elif star["y"] > camera_bounding_box[3]:
                star["y"] = camera_bounding_box[1]
                star["x"] = random.randint(self.camera.camera_x - 640, self.camera.camera_y + 640)

        # Update meteors
        for shooting_star in self.shooting_stars:
            shooting_star["x"] += math.cos(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time
            shooting_star["y"] += math.sin(math.radians(shooting_star["direction"])) * shooting_star["speed"] * delta_time

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

        # Spawn new meteor
        if random.randint(0, 300) == 0:
            self.spawn_new_meteor()

    def spawn_new_meteor(self):
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

    def draw(self, surface: pygame.Surface) -> None:
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

        # Render placeholder player
        position = self.entity_manager.get_component(self.player_id, Position)
        pygame.draw.rect(surface, (255, 0, 0), ((590, 310, 100, 100)))

    def stop(self) -> None:
        pass