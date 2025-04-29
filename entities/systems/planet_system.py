# Built-ins
from __future__ import annotations
import random

# External
import pygame
from pygame.locals import *
import math
import time

# Internal
from pygamelib.entities import *
from entities import *
from utils.constants import *

class Planet:
    def __init__(self, name: str, surface_image: pygame.Surface, radius: int, day: float, year: float, kind:str, dist: int, mass: int, orbits: object | None, rotation_direction: str) -> None:
        self.name = name

        self.radius = math.floor(math.sqrt(radius))
        self.diameter = self.radius * 2

        self.day = day # in hours
        self.year = year # in day

        self.kind = kind

        if self.kind == "moon":
            self.dist = dist * 1.5
        else:
            self.dist = math.sqrt(dist) * math.sqrt(57909) / 5

        self.mass = mass * 150

        self.orbits = orbits

        self.theta = random.randint(0, 359) # the angle on the orbit

        self.x, self.y = 0, 0

        self.rotation_direction = rotation_direction

        # rendering stuff
        self.surface_image = surface_image
        self.surface_image_size = surface_image.get_size()
        self.surface_image_center = (self.surface_image_size[0] / 2, self.surface_image_size[1] / 2)

        self.surface_center = (self.radius, self.radius)

        self.surface_size = (self.surface_center[0] * 2, self.surface_center[1] * 2)

        # self.revolution_time = revolution_time

        self.circle_mask = pygame.Surface(self.surface_size)
        self.circle_mask.fill((0, 0, 0))
        pygame.draw.circle(self.circle_mask, (1, 1, 1), self.surface_center, self.radius)
        self.circle_mask.set_colorkey((1, 1, 1))

        width, height = surface_image.get_size()
        self.image_offsets = []

        if self.diameter == height:
            for xi in range(math.ceil(self.diameter / width) + 3):
                self.image_offsets.append(pygame.Vector2((-self.radius - (width / 2) - width) + xi * width, 0))
        else:
            for xi in range(math.ceil(self.diameter / width) + 3):
                for yi in range(math.ceil(math.ceil((self.diameter / height)) + 1)):
                    self.image_offsets.append(pygame.Vector2((-self.radius - (width / 2) - width) + xi * width, (-self.radius) + yi * height))

        width = (math.ceil(self.diameter / width) + 3) * width / 2

        if self.rotation_direction == "clockwise":
            self.borders = (-width, width)
        else:
            self.borders = (width, -width)

        self.surface = pygame.Surface(self.surface_size)

        self.on_screen = False

        # Mission data
        self.missions = []

#this class is intended solely for flight path predictions
class PlanetImprint:
    def __init__(self, radius: int, day: float, year: float, kind: str, dist: int, mass: int, orbits: object | None, theta: float | int) -> None:
        self.radius = radius
        self.diameter = self.radius * 2

        self.day = day # in hours
        self.year = year # in day

        self.kind = kind

        self.dist = dist

        self.mass = mass

        self.orbits = orbits

        self.theta = theta

        self.x, self.y = 0, 0

def from_planet_to_imprint(planet:Planet) -> PlanetImprint:
    return PlanetImprint(planet.radius, planet.day, planet.year, planet.kind, planet.dist, planet.mass, planet.orbits, planet.theta)

class PlanetHandler:
    def handle_event(self, entity_manager, camera: CameraSystem, event):
        if event.type == MOUSEBUTTONDOWN:
            entity_ids = entity_manager.get_from_components(Planet)

            for entity_id in entity_ids:
                planet: Planet = entity_manager.get_component(entity_id, Planet)
                pos = camera.get_relative_position((planet.x - planet.radius, planet.y - planet.radius))

                if pygame.rect.Rect(pos[0], pos[1], planet.radius * 2, planet.radius * 2).collidepoint(event.pos):
                    camera.selected_planet = planet
                    camera.changed = True
                    return
                
            camera.selected_planet = None
            camera.changed = True

    def update(self, entity_manager: EntityManager, camera: CameraSystem, delta_time: float):
        entity_ids = entity_manager.get_from_components(Planet, CircleCollider)

        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            circle:CircleCollider = entity_manager.get_component(entity_id, CircleCollider)

            if planet.orbits is not None:
                planet.theta = (delta_time/planet.year*24*GAMEH_PER_REALSEC + planet.theta)%360

                orbit:Planet = entity_manager.get_component(planet.orbits, Planet)

                planet.x, planet.y = orbit.x + (planet.dist + orbit.radius + planet.radius)*math.cos(planet.theta*math.pi/180), orbit.y + (planet.dist + orbit.radius + planet.radius)*math.sin(planet.theta*math.pi/180)
            
            circle.x, circle.y = planet.x, planet.y

            if math.sqrt(((planet.x - camera.camera_x) ** 2) + ((planet.y - camera.camera_y) ** 2)) < 1280 + planet.radius:
                planet.surface.fill((0, 0, 0))
                planet.surface.set_colorkey((0, 0, 0))

                dx = delta_time/planet.day*GAMEH_PER_REALSEC * planet.diameter

                for i in range(len(planet.image_offsets)):
                    if planet.rotation_direction == "clockwise":
                        planet.image_offsets[i].x += dx
                        if planet.image_offsets[i].x > planet.borders[1]:
                            planet.image_offsets[i].x = planet.borders[0] + (planet.image_offsets[i].x - planet.borders[1])
                    else:
                        planet.image_offsets[i].x -= dx
                        if planet.image_offsets[i].x < planet.borders[1]:
                            planet.image_offsets[i].x = planet.borders[0] + (planet.image_offsets[i].x - planet.borders[1])

                for image_offset in planet.image_offsets:
                    position = (math.floor(planet.surface_center[0] + image_offset.x), math.floor(planet.surface_center[1] + image_offset.y))
                    planet.surface.blit(planet.surface_image, planet.surface_image.get_rect(center = position))

                planet.surface.blit(planet.circle_mask, planet.circle_mask.get_rect(center = planet.surface_center))

                planet.on_screen = True

            else:
                
                planet.on_screen = False

    def draw(self, entity_manager: EntityManager, camera: CameraSystem, display_surface: pygame.Surface):
        entity_ids = entity_manager.get_from_components(Planet)
        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            if planet.on_screen:
                if camera.selected_planet == planet:
                    render_pos = (camera.internal_surface.size[0] / 2, camera.internal_surface.size[1] / 2)
                    pygame.draw.circle(display_surface, (255, 255, 255), render_pos, planet.radius + 2)

                else:
                    render_pos = camera.get_relative_position((planet.x, planet.y))

                display_surface.blit(planet.surface, planet.surface.get_rect(center = render_pos))

    def get_planet_imprints(self, entity_manager: EntityManager) -> dict[int:PlanetImprint]:
        planet_imprints = {}

        entity_ids = entity_manager.get_from_components(Planet)

        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            planet_imprints[entity_id] = from_planet_to_imprint(planet)

        return planet_imprints