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

    def update(self, entity_manager: EntityManager, player_id: int, planet_ids: list[int], planet_imprints, delta_time) -> None:
        self.map.update(entity_manager, player_id, planet_ids, planet_imprints, delta_time)

    def draw(self, surface: pygame.Surface):
        self.map.draw(surface)

class Map:
    def __init__(self):
        self.map_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.map_surface_center = pygame.Vector2(self.map_surface.get_rect().size) / 2

        self.map_mode = 0
        self.fullscreened = False
        self.panning = False

        self.zoom = 1.0
        self.lastpos = (0, 0)
        self.offset = pygame.Vector2(0, 0)

        self.planet_imprint_handler = PlanetImprintHandler()

    def handle_event(self, event):
        if event.type == MOUSEWHEEL:
            if event.y == 1:
                self.set_zoom(self.zoom - 0.1)

            elif event.y == -1:
                self.set_zoom(self.zoom + 0.1)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.panning = True
                self.last_pos = event.pos

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.panning = False

        elif event.type == KEYDOWN:
            if event.key == K_UP:
                self.set_zoom(self.zoom - 0.1)

            elif event.key == K_DOWN:
                self.set_zoom(self.zoom + 0.1)

            elif event.key == K_m:
                if self.map_mode == 0:
                    self.set_mode(1)

                else:
                    self.set_mode(0)

            elif event.key == K_TAB:
                self.fullscreened = not self.fullscreened
                self.set_zoom(1)

            elif event.key == K_v:
                if self.map_mode == 1:
                    self.set_mode(2)

                elif self.map_mode == 2:
                    self.set_mode(1)

            elif event.key == K_r:
                self.set_zoom(1)
                self.offset.x, self.offset.y = 0, 0

    def set_zoom(self, new_zoom):
        self.zoom = max(new_zoom, 0.01)
        # self.map_surface = pygame.Surface((1280 * self.zoom, 720 * self.zoom))
        # self.map_surface_center = pygame.Vector2(self.map_surface.get_rect().size) / 2

    def set_mode(self, new_mode):
        self.map_mode = new_mode
        self.set_zoom(1)

    def update(self, entity_manager: EntityManager, player_id:int, planet_ids:list[int], planet_imprints:dict[int:PlanetImprint], delta_time: int | float):
        self.map_surface.fill((50, 50, 50))
        if self.fullscreened:
            if self.panning:
                new_pos = pygame.Vector2(pygame.mouse.get_pos())
                self.offset -= new_pos - self.last_pos
                self.last_pos = new_pos

            offset = self.offset

        else:
            offset = pygame.Vector2(0, 0)
            self.set_zoom(1)

        def calculate_scale(self, value:int|float):
            return value * self.zoom

        def calculate_on_map_position(self, position:pygame.Vector2):
            return self.map_surface_center[0] + calculate_scale(self, position.x / 460), self.map_surface_center[1] + calculate_scale(self, position.y / 460)

        if self.map_mode == 1:
            #pass one to draw orbit tracks
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                if planet.kind != "moon":
                    center = self.map_surface_center - offset
                    if planet.orbits == None:
                        pygame.draw.circle(self.map_surface, (235, 222, 52), center, calculate_scale(self, planet.dist / 460) + max(calculate_scale(self, planet.radius / 460), 5), 2)
                    else:
                        orbit:Planet = entity_manager.get_component(planet.orbits, Planet)
                        pygame.draw.circle(self.map_surface, (235, 222, 52), center, calculate_scale(self, planet.dist / 460) + calculate_scale(self, planet.radius / 460) + calculate_scale(self, orbit.radius / 460), 2)
            
            #pass two drawing moon orbit
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                if planet.kind == "moon":
                    orbit:Planet = entity_manager.get_component(planet.orbits, Planet)
                    center = calculate_on_map_position(self, pygame.Vector2(orbit.x, orbit.y)) - offset
                    pygame.draw.circle(self.map_surface, (235, 222, 52), center, calculate_scale(self, planet.dist / 460) + calculate_scale(self, planet.radius / 460) + calculate_scale(self, orbit.radius / 460), 2)
            
            #pass three to draw planet positions

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                on_map_position = calculate_on_map_position(self, pygame.Vector2(planet.x, planet.y))

                if planet.kind == "moon":
                    pygame.draw.circle(self.map_surface, (235, 52, 201), on_map_position - offset, max(calculate_scale(self, planet.radius / 460), 4))
                else:
                    pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position - offset, max(calculate_scale(self, planet.radius / 460), 5))

            position:Position = entity_manager.get_component(player_id, Position)

            on_map_position = (self.map_surface_center[0] + calculate_scale(self, position.x / 460), self.map_surface_center[1] + calculate_scale(self, position.y / 460))

            pygame.draw.circle(self.map_surface, (0, 0, 255), on_map_position  - offset, min(max(calculate_scale(self, 4), 4), 4))

        elif self.map_mode == 2:
            for i in range(10):
                self.planet_imprint_handler.update(planet_imprints, delta_time * 10)

            player_position:Position = entity_manager.get_component(player_id, Position)

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                on_map_position = (self.map_surface_center[0] + calculate_scale(self, (planet.x - player_position.x) / 4), self.map_surface_center[1] + calculate_scale(self, (planet.y - player_position.y) / 4))

                pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position, calculate_scale(self, planet.radius / 4))

            pygame.draw.circle(self.map_surface, (0, 0, 255), self.map_surface_center, 5)

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
            self.draw_overlay(surface)

    def draw_orbits(self): # Move from update into here (maybe cache new values of planets in update and render here)
        pass

    def draw_planets(self): # Move from update into here (maybe cache new values of planets in update and render here)
        pass

    def draw_overlay(self, surface: pygame.Surface):
        display_surface = pygame.transform.smoothscale(self.map_surface, (400, 225))
        surface.blit(display_surface, (0, 0))

    def draw_fullscreen(self, surface: pygame.Surface):
        display_surface = pygame.transform.smoothscale(self.map_surface, (1280, 720))
        surface.blit(display_surface, display_surface.get_rect(center = (surface.get_width() - 1280 / 2, 720 / 2)))