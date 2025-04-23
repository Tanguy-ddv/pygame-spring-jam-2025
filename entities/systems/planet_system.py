# External
import pygame
import math

# Internal
from pygamelib.entities import *
from entities import *
from .bloom_system import Bloom

class Planet:
    def __init__(self, planet_radius:int, surface_image:pygame.Surface, atmosphere_radius:int, atmosphere_colour:tuple, revolution_speed:int):
        self.surface_image = surface_image

        self.planet_radius = planet_radius

        self.surface_center = (planet_radius + atmosphere_radius, planet_radius + atmosphere_radius)
        self.surface_size = (self.surface_center[0] * 2, self.surface_center[1] * 2)

        self.circle_mask = pygame.Surface(self.surface_size)
        self.circle_mask.fill((0, 0, 0))
        pygame.draw.circle(self.circle_mask, (1, 1, 1), self.surface_center, self.planet_radius)
        self.circle_mask.set_colorkey((1, 1, 1))

        self.image_offsets = [-80, 0, 80]

        self.atmosphere_image = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        self.atmosphere_image.set_colorkey((0, 0, 0))

        for i in range(self.planet_radius + atmosphere_radius):
            color_factor = i / (self.planet_radius + atmosphere_radius)
            pygame.draw.circle(self.atmosphere_image, (atmosphere_colour[0] * color_factor, atmosphere_colour[1] * color_factor, atmosphere_colour[2] * color_factor), self.surface_center, self.planet_radius + atmosphere_radius - i)

        self.revolution_speed = revolution_speed

class PlanetRenderer:
    def update(self, entity_manager: EntityManager, delta_time: float):
        entity_ids = entity_manager.get_from_components(Planet, pygame.Surface)
        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            surface:pygame.Surface = entity_manager.get_component(entity_id, pygame.Surface)

            surface.fill((0, 0, 0))
            surface.set_colorkey((0, 0, 0))

            for i in range(len(planet.image_offsets)):
                planet.image_offsets[i] += planet.revolution_speed * delta_time
                if planet.image_offsets[i] > 120:
                    planet.image_offsets[i] = -120

            for image_offset in planet.image_offsets:
                position = (planet.surface_center[0] + image_offset, planet.surface_center[1] + math.sin(45))
                surface.blit(planet.surface_image, planet.surface_image.get_rect(center = position))
            surface.blit(planet.circle_mask, planet.circle_mask.get_rect(center = planet.surface_center))

        entity_ids = entity_manager.get_from_components(Planet, Bloom)
        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            surface:Bloom = entity_manager.get_component(entity_id, Bloom)

            surface.fill((0, 0, 0))
            surface.blit(planet.atmosphere_image)

