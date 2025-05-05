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
from assets import Fonts, Images
from utils.constants import *

class Planet:
    def __init__(self, reputation, name: str, surface_image: pygame.surface.Surface, radius: int, day: float, year: float, kind:str, dist: int, mass: int, orbits: object | None, rotation_direction: str) -> None:
        self.reputation = reputation
        self.name = name

        self.radius = math.floor(math.sqrt(radius))
        self.diameter = self.radius * 2

        self.day = day # in hours
        self.year = year # in day

        self.kind = kind

        if "moon" in self.kind:
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

        self.circle_mask = pygame.surface.Surface(self.surface_size)
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

        self.surface = pygame.surface.Surface(self.surface_size)

        self.on_screen = False

        # Mission data
        self.mission_dict = {}
        if self.kind != "sun":
            for _ in range(6):
                mission = new_mission(self.reputation, self.name)
                self.mission_dict[mission] = self._render_mission(mission)

    def _render_mission(self, mission):
        font = Fonts.get_font("Small")
        if mission.type == "kill":
            surface = pygame.surface.Surface((1280 / 3, font.get_height() * 3.5), SRCALPHA)
            pygame.draw.rect(surface, (30, 30, 30), (0, 0, 1280 / 3, font.get_height() * 3.5), 0, 5)
            title = font.render(
                f"Bounty hunting : ${mission.reward}",
                True,
                (150, 255, 150)
            )

            surface.blit(title, (0, 0))
            surface.blit(font.render(
                f"Eliminate {mission.max_amount} {mission.item}\nnear {mission.destination}\n",
                True,
                (255, 255, 255)
            ), (0, 5 + title.get_height()))

        elif mission.type == "delivery":
            surface = pygame.surface.Surface((1280 / 3, font.get_height() * 3.5), SRCALPHA)
            pygame.draw.rect(surface, (30, 30, 30), (0, 0, 1280 / 3, font.get_height() * 3.5), 0, 5)
            title = font.render(
                f"Shipment Order  : ${mission.reward}",
                True,
                (150, 255, 150)
            )

            surface.blit(title, (0, 0))
            surface.blit(font.render(
                f"Deliver {mission.max_amount}{mission.unit} of\n{mission.item} to {mission.destination}\n",
                True,
                (255, 255, 255)
            ), (0, 5 + title.get_height()))

        elif mission.type == "complete":
            surface = pygame.surface.Surface((1280 / 3, font.get_height() * 3))
            pygame.draw.rect(surface, (30, 30, 30), (0, 0, 1280 / 3, font.get_height() * 3), 0, 5)
            surface.blit(font.render(
                f"${mission.reward} reward\n at {mission.destination}",
                True,
                (150, 255, 150)
            ), (0, 0))

        else:
            surface = self.mission_dict[mission]

        text = Images.get_image("accept")
        surface.blit(text, (1280 / 3 - text.get_width() - 8, font.get_height() * 3.5 - text.get_height() - 5))

        return surface

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
    def update(self, entity_manager: EntityManager, hud, camera: CameraSystem, delta_time: float, paused=False):
        entity_ids = entity_manager.get_from_components(Planet, CircleCollider)

        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            circle:CircleCollider = entity_manager.get_component(entity_id, CircleCollider)

            if paused:
                if planet.on_screen:
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

                continue
            
            if planet.orbits is not None:
                planet.theta = (delta_time/planet.year*24*GAMEH_PER_REALSEC + planet.theta)%360

                orbit:Planet = entity_manager.get_component(planet.orbits, Planet)

                planet.x, planet.y = orbit.x + (planet.dist + orbit.radius + planet.radius)*math.cos(planet.theta*math.pi/180), orbit.y + (planet.dist + orbit.radius + planet.radius)*math.sin(planet.theta*math.pi/180)
            
            circle.x, circle.y = planet.x, planet.y

            show_waypoint = False

            for mission in hud.log.mission_dict:
                if planet.name in mission.destination:
                    show_waypoint = True
            
            if show_waypoint:
                if entity_manager.has_component(entity_id, Waypoint):
                    waypoint:Waypoint = entity_manager.get_component(entity_id, Waypoint)
                    waypoint.position.xy = planet.x, planet.y
                    waypoint.max_viewable_distance = None
                else:
                    entity_manager.add_component(entity_id, Waypoint(pygame.Vector2(planet.x, planet.y), None, (0, 255, 0)))
            else:
                entity_manager.remove_component(entity_id, Waypoint)

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

    def draw(self, entity_manager: EntityManager, camera: CameraSystem, display_surface: pygame.surface.Surface):
        entity_ids = entity_manager.get_from_components(Planet)
        for entity_id in entity_ids:
            planet:Planet = entity_manager.get_component(entity_id, Planet)
            if planet.on_screen:
                if camera.selected_planet == planet:
                    render_pos = (camera.internal_surface.get_size()[0] / 2, camera.internal_surface.get_size()[1] / 2)
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