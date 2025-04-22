# External
import pygame
from pygame.locals import *

# Internal
from pygamelib.entities import *
from entities import *

class InputSystem:
    def handle_event(self, entity_manager, entity_id: int, event: pygame.Event):
        if event.type == KEYDOWN:
            self.key_pressed(entity_manager, entity_id, event)

    def key_pressed(self, entity_manager: EntityManager, entity_id: int, event: pygame.Event):
        if not entity_manager.has_component(entity_id, Force):
            return
        
        if event.key == K_w:
            force = Force(0, -50)

        elif event.key == K_a:
            force = Force(-50, 0)

        elif event.key == K_s:
            force = Force(0, 50)

        elif event.key == K_d:
            force = Force(50, 0)

        entity_manager.add_component(entity_id, force)

    def update(self):
        pass