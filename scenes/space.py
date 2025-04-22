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
        self.entity_manager.add_component(self.player_id, Rotation(0))

        # Player surface
        self.entity_manager.add_component(self.player_id, Images.get_image("player"))

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


    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))

        self.background_system.draw(surface, self.camera, Images)
        self.camera.draw(surface, self.entity_manager)

    def stop(self) -> None:
        pass