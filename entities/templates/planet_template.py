import pygame
from entities import *
from pygamelib import *
from .entity_template import create_entity

def create_planet(entity_manager:EntityManager, position:tuple, radius:int, surface_image:pygame.Surface, atmosphere_radius:int, atmosphere_color:tuple, revolution_speed:int):
    return create_entity(entity_manager, 
                         Position(position), 
                         Planet(radius, surface_image, atmosphere_radius, atmosphere_color, revolution_speed),
                         pygame.Surface((radius * 2 + atmosphere_radius * 2, radius * 2 + atmosphere_radius * 2), pygame.SRCALPHA),
                         Bloom((radius * 2 + atmosphere_radius * 2, radius * 2 + atmosphere_radius * 2), pygame.SRCALPHA)
                         )

