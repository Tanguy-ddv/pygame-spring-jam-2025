# External
import pygame
from pygame.locals import *

# Internal
from pygamelib.entities import *
from entities import *

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

    def update(self):
        for key, key_data in self.held_keys.items():
            entity_manager, entity_id = key_data
            force = entity_manager.get_component(entity_id, Force)

            if key == K_w:
                force += Force(0, -25)

            elif key == K_a:
                force += Force(-25, 0)

            elif key == K_s:
                force += Force(0, 25)

            elif key == K_d:
                force += Force(25, 0)

            entity_manager.add_component(entity_id, force)