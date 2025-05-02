# External
import pygame
from pygame.locals import *
import math
import time
import random

# Internal
from pygamelib.entities import *
from entities import *

from assets import *

from .camera_system import CameraSystem

class ShieldRenderer:
    def draw(self, entity_manager: EntityManager, camera_system: CameraSystem):
        entity_ids = entity_manager.get_from_components(Position, Shield, Fuel)
        for entity_id in entity_ids:
            if entity_manager.has_component(entity_id, Dying):
                continue
            
            shield:Shield = entity_manager.get_component(entity_id, Shield)
            position = entity_manager.get_component(entity_id, Position)
            fuel: Fuel = entity_manager.get_component(entity_id, Fuel)

            if shield.activated and fuel.fuel > 0:
                surface = Images.get_image("shield")
                camera_system.get_surface().blit(surface, surface.get_rect(center = camera_system.get_relative_position(position.xy)))