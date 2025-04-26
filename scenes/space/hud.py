# Built-ins

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *

class HUD:
    def __init__(self):
        # Toggle HUD
        self.enabled = True

        # Map
        self.map = Map()

    def handle_event(self, event):
        self.map.handle_event(event)

    def update(self, entity_manager: EntityManager, player_id: int, planet_ids: list[int]) -> None:
        self.map.update(entity_manager, player_id, planet_ids)

    def draw(self, surface: pygame.Surface):
        self.map.draw(surface)

class Map:
    def __init__(self):
        self.map_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.map_surface_center = pygame.Vector2(self.map_surface.get_rect().size) / 2

        self.map_mode = 0
        self.fullscreened = True
        self.zoom = 1.0

    def handle_event(self, event):
        if event.type == MOUSEWHEEL:
            if event.y == 1:
                self.set_zoom(self.zoom - 0.1)

            elif event.y == -1:
                self.set_zoom(self.zoom + 0.1)

        elif event.type == KEYDOWN:
            if event.key == K_UP:
                self.set_zoom(self.zoom - 0.1)

            elif event.key == K_DOWN:
                self.set_zoom(self.zoom + 0.1)

    def set_zoom(self, new_zoom):
        self.zoom = max(new_zoom, 0.01)
        self.map_surface = pygame.Surface((1280 * self.zoom, 720 * self.zoom))
        self.map_surface_center = pygame.Vector2(self.map_surface.get_rect().size) / 2

    def update(self, entity_manager: EntityManager, player_id:int, planet_ids:list[int]):
        self.map_surface.fill((50, 50, 50))
        offset = pygame.mouse.get_pos() - pygame.Vector2(1280, 720) / 2

        if self.map_mode == 1:
            #pass one to draw orbit tracks

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                if planet.kind != "moon":
                    pygame.draw.circle(self.map_surface, (235, 222, 52), self.map_surface_center - offset, planet.dist / 8000, 2)
            
            #pass two to draw planet positions

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                if planet.kind != "moon":
                    on_map_position = (self.map_surface_center[0] + (planet.x / 8000), self.map_surface_center[1] + (planet.y / 8000))

                    pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position  - offset, 2)

            position:Position = entity_manager.get_component(player_id, Position)

            on_map_position = (self.map_surface_center[0] + (position.x / 8000), self.map_surface_center[1] + (position.y / 8000))

            pygame.draw.circle(self.map_surface, (0, 0, 255), on_map_position  - offset, 3)

        elif self.map_mode == 2:
            player_position:Position = entity_manager.get_component(player_id, Position)

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                on_map_position = (self.map_surface_center[0] + ((planet.x - player_position.x) / 16), self.map_surface_center[1] + ((planet.y - player_position.y) / 16))

                pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position, planet.radius / 16)

            pygame.draw.circle(self.map_surface, (0, 0, 255), self.map_surface_center, 3)

    def draw(self, surface: pygame.Surface):
        if self.map_mode == 0:
            return
        
        elif self.map_mode == 1:
            self.draw_orbits()

        elif self.map_mode == 2:
            self.draw_planets()

        if self.fullscreened:
            self.draw_fullscreen(surface)

        else:
            self.draw_orbits(surface)

    def draw_orbits(self): # Move from update into here (maybe cache new values of planets in update and render here)
        pass

    def draw_planets(self): # Move from update into here (maybe cache new values of planets in update and render here)
        pass

    def draw_overlay(self, surface: pygame.Surface):
        pass

    def draw_fullscreen(self, surface: pygame.Surface):
        display_surface = pygame.transform.smoothscale(self.map_surface, (1280, 720))
        surface.blit(display_surface, display_surface.get_rect(center = (surface.get_width() - 1280 / 2, 720 / 2)))