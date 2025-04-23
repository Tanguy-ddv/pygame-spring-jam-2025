# Built-ins
import random

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
        self.background_system = BackgroundSystem()
        self.physics_system = PhysicsSystem()
        self.planet_renderer = PlanetRenderer()
        self.bloom_system = BloomSystem()

        self.camera = CameraSystem((1280, 720), (640, 360))

        # Test planet
        self.test_planet_id = create_planet(self.entity_manager, (320, 180), 40, Images.get_image("test"), 50, (0, 0, 75))

        # Player
        self.player_id = create_entity(self.entity_manager, 
                                       Listener({KEYDOWN: [self.input_system], KEYUP: [self.input_system]}),
                                       Position(640, 360),
                                       Velocity(0, 0),
                                       Force(0, 0),
                                       Mass(1),
                                       Rotation(0),
                                       Images.get_image("player")
                                       )

    def start(self) -> None:
        pass

    def handle_events(self, events: list[pygame.Event]) -> None:
        self.event_system.handle_events(self.entity_manager, events)

    def update(self, delta_time: float) -> None:
        self.input_system.update(delta_time)
        self.physics_system.update(self.entity_manager, delta_time)
        self.camera.set_position(self.entity_manager.get_component(self.player_id, Position))

        # Update stars
        self.background_system.update(self.camera, delta_time)

        self.planet_renderer.update(self.entity_manager, delta_time)


    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))

        self.background_system.draw(surface, self.camera, Images)
        self.camera.draw(surface, self.entity_manager)
        self.bloom_system.draw(self.camera, surface, self.entity_manager)

    def stop(self) -> None:
        pass