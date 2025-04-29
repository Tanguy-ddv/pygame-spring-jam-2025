# External
import pygame
from pygame.locals import *
import math
import time
import random

# Internal
from pygamelib.entities import *
from entities import *
from utils.constants import *

from assets import *

from .camera_system import CameraSystem

class ShieldRenderer:
    def draw(self, entity_manager: EntityManager, camera_system: CameraSystem):
        entity_ids = entity_manager.get_from_components(Position, Shield)
        for entity_id in entity_ids:
            if entity_manager.has_component(entity_id, Dying):
                continue
            
            shield:Shield = entity_manager.get_component(entity_id, Shield)
            position = entity_manager.get_component(entity_id, Position)
            if shield.activated:
                surface = Images.get_image("shield")
                camera_system.get_surface().blit(surface, surface.get_rect(center = camera_system.get_relative_position(position.xy)))