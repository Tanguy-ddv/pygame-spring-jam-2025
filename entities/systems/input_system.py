# Built-ins
import math

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib.entities import *
from entities import *
from assets import Images


# from ..templates import create_entity

class InputSystem:
    def __init__(self):
        self.held_keys: dict[int, tuple[EntityManager, int]] = {}
        
    def handle_event(self, entity_manager, entity_id: int, event: pygame.Event):
        if event.type == KEYDOWN:
            self.key_pressed(entity_manager, entity_id, event)

        elif event.type == KEYUP:
            self.key_unpressed(event)

    def key_pressed(self, entity_manager: EntityManager, entity_id: int, event: pygame.Event):
        if event.key in self.held_keys.keys():
            return
        
        self.held_keys[event.key] = (entity_manager, entity_id)

    def key_unpressed(self, event: pygame.Event):
        if event.key in self.held_keys:
            self.held_keys.pop(event.key)

    def update(self, delta_time):
        for key, key_data in self.held_keys.items():
            entity_manager, entity_id = key_data
            force = entity_manager.get_component(entity_id, Force)
            velocity = entity_manager.get_component(entity_id, Velocity)
            rotation = entity_manager.get_component(entity_id, Rotation)

            # Apply thruster force
            if key == K_SPACE:
                force.x += 25 * math.cos(math.radians(rotation.angle))
                force.y -= 25 * math.sin(math.radians(rotation.angle))
            
            # Rotate spaceship ACW
            if key == K_a:
                rotation.angle = (rotation.angle + (120 * delta_time)) % 360

            # Rotate spaceship CW
            if key == K_d:
                rotation.angle = (rotation.angle - (120 * delta_time)) % 360

            print(rotation.angle)
            print(velocity.xy)
            entity_manager.add_component(entity_id, pygame.transform.rotate(Images.get_image("player"), rotation.angle))