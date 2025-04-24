import random

# External
import pygame
import math
import time

# Internal
from pygamelib.entities import *
from entities import *
from .bloom_system import Bloom
from utils.constants import *

class Planet:
    def __init__(self, name: str, path: str, radius: int, day: float, year: float, dist: int, orbits: object | None) -> None:
        self.name = name
        self.path = path
        self.radius = radius/15
        self.day = day # in hours
        self.year = year # in day
        self.dist = math.sqrt(dist)
        self.orbits = orbits
        self.theta = random.randint(0, 359) # the angle on the orbit
        self.phi = random.randint(0, 359) # the spinning angle
        if self.orbits is None:
            self.cx, self.cy = 0, 0
        else:
            self.cx, self.cy = self.orbits.cx + self.dist*math.cos(self.theta*math.pi/180), self.orbits.cy + self.dist*math.sin(self.theta*math.pi/180)
    
    def update(self, dt: float):
        # dt is in sec
        self.phi = (dt/self.day*GAMEH_PER_REALSEC + self.phi)%360
        if self.orbits is not None:
            self.theta = (dt/self.year*24*GAMEH_PER_REALSEC + self.theta)%360
            self.cx, self.cy = self.orbits.cx + self.dist*math.cos(self.theta*math.pi/180), self.orbits.cy + self.dist*math.sin(self.theta*math.pi/180)

class Temp_Planet:
    def __init__(self, planet_radius:int, surface_image:pygame.Surface, body_color:tuple, atmosphere:int, atmosphere_colour:tuple, revolution_time:int = 10):
        self.surface_image = surface_image
        self.surface_image_size = surface_image.get_size()
        self.surface_image_center = (self.surface_image_size[0] / 2, self.surface_image_size[1] / 2)
        
        self.planet_radius = planet_radius
        self.planet_diameter = (planet_radius * 2)

        self.surface_center = (planet_radius + atmosphere, planet_radius + atmosphere)
        self.surface_size = (self.surface_center[0] * 2, self.surface_center[1] * 2)

        self.body_color = body_color

        self.revolution_time = revolution_time

        self.circle_mask = pygame.Surface(self.surface_size)
        self.circle_mask.fill((0, 0, 0))
        pygame.draw.circle(self.circle_mask, (1, 1, 1), self.surface_center, self.planet_radius)
        self.circle_mask.set_colorkey((1, 1, 1))

        width, height = surface_image.get_size()
        self.image_offsets = []

        for xi in range(math.ceil(self.planet_diameter / width) + 3):
            for yi in range(math.ceil((self.planet_diameter / height)) + 1):
                self.image_offsets.append(pygame.Vector2((-self.planet_radius - (width / 2) - width) + xi * width, (-planet_radius) + yi * height))

        self.borders = (-self.planet_radius - (width / 2), self.planet_radius + (width / 2))

        self.atmosphere_image = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        self.atmosphere_image.set_colorkey((0, 0, 0))

        for i in range(self.planet_radius + atmosphere):
            color_factor = i / (self.planet_radius + atmosphere)
            pygame.draw.circle(self.atmosphere_image, (atmosphere_colour[0] * color_factor, atmosphere_colour[1] * color_factor, atmosphere_colour[2] * color_factor), self.surface_center, self.planet_radius + atmosphere - i)

class PlanetRenderer:
    def update(self, entity_manager: EntityManager, delta_time: float):
        entity_ids = entity_manager.get_from_components(Temp_Planet, pygame.Surface)
        for entity_id in entity_ids:
            planet:Temp_Planet = entity_manager.get_component(entity_id, Temp_Planet)
            surface:pygame.Surface = entity_manager.get_component(entity_id, pygame.Surface)

            surface.fill(planet.body_color)
            surface.set_colorkey((0, 0, 0))

            for i in range(len(planet.image_offsets)):
                planet.image_offsets[i].x += planet.revolution_time * delta_time
                if planet.image_offsets[i].x > planet.borders[1]:
                    planet.image_offsets[i].x = planet.borders[0] + (planet.image_offsets[i].x - planet.borders[1])

            for image_offset in planet.image_offsets:
                position = (math.floor(planet.surface_center[0] + image_offset.x), math.floor(planet.surface_center[1] + image_offset.y))
                surface.blit(planet.surface_image, planet.surface_image.get_rect(center = position))

            surface.blit(planet.circle_mask, planet.circle_mask.get_rect(center = planet.surface_center))

        entity_ids = entity_manager.get_from_components(Temp_Planet, Bloom)
        for entity_id in entity_ids:
            planet:Temp_Planet = entity_manager.get_component(entity_id, Temp_Planet)
            surface:Bloom = entity_manager.get_component(entity_id, Bloom)

            surface.fill((0, 0, 0))
            surface.blit(planet.atmosphere_image)

