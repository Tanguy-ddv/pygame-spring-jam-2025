import pygame
from entities import *
from pygamelib import *
from .camera_system import CameraSystem

class Bloom(pygame.Surface):
    pass

class BloomSystem:
    def __init__(self):
        pass
        
    def draw(self, camera:CameraSystem, display_surface:pygame.Surface, entity_manager:EntityManager):
        entity_ids = entity_manager.get_from_components(Bloom, Position)

        for entity_id in entity_ids:
            surface = entity_manager.get_component(entity_id, Bloom)
            position = entity_manager.get_component(entity_id, Position)

            display_surface.blit(surface, surface.get_rect(center = camera.get_relative_position(position)), special_flags=pygame.BLEND_RGB_ADD)