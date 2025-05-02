# Built-ins

# External
import pygame
import math
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *
from assets import *
from utils.constants import GAMEH_PER_REALSEC

class HUD:
    def __init__(self):
        # Elements
        self.map = Map()
        self.planet_interface = PlanetInterface()
        self.manual = Manual()
        self.log = Log()
        self.fuel_display = FuelDisplay()

    def handle_event(self, event):
        if self.planet_interface.planet == None:
            self.map.handle_event(event)
            self.manual.handle_event(event)
            self.log.handle_event(event)

        self.planet_interface.handle_event(event)

    def update(self, entity_manager: EntityManager, player_id: int, planet_ids: list[int], future_player_positions: list[tuple], pirate_handler: PirateHandler, camera, delta_time) -> None:
        self.map.update(entity_manager, player_id, planet_ids, future_player_positions, pirate_handler)
        self.manual.update(delta_time)
        self.log.update(delta_time)
        self.planet_interface.update(camera, delta_time)
        self.fuel_display.update(entity_manager, player_id, delta_time)

    def draw(self, surface: pygame.Surface):
        if self.manual.enabled:
            self.manual.draw(surface)

        elif self.planet_interface.enabled:
            self.planet_interface.draw(surface)

        elif self.map.fullscreened and self.map.map_mode != 0:
            self.map.draw(surface)

        else:
            self.map.draw(surface)
            self.log.draw(surface)
            self.fuel_display.draw(surface)

class FuelDisplay:
    def __init__(self):
        self.target_fuel_level = 1
        self.fuel_level = 1
        self.initial_fuel_level = 1

        self.time_elapsed = 0
        self.widget_center = (225, 25)
        self.widget_size = (500, 50)
        self.widget_rect = pygame.rect.FRect(self.widget_center[0] - self.widget_size[0] / 2, self.widget_center[1] - self.widget_size[1] / 2, self.widget_size[0], self.widget_size[1])
        self.color_a = [240, 240, 40]
        self.color = self.color_a.copy()
        self.render_time = 0
        self.text = Fonts.get_font("Body").render("POWER : 100%", True, "#222222")

    def update(self, entity_manager, player_id, delta_time):
        self.time_elapsed += delta_time

        fuel = entity_manager.get_component(player_id, Fuel)
        last_target = self.target_fuel_level

        self.target_fuel_level = fuel.fuel / fuel.max_fuel
        if last_target != self.target_fuel_level:
            self.time_elapsed = 0
            self.initial_fuel_level = self.fuel_level

        last_fuel = self.fuel_level
        self.fuel_level = min(self.target_fuel_level, self.initial_fuel_level + (self.target_fuel_level - self.initial_fuel_level) * abs(math.sin(math.radians(min(self.time_elapsed * 90, 90)))))

        if self.fuel_level != last_fuel:
            self.render_time += delta_time
            self.color[2] = 40 + abs(math.sin(math.radians(self.render_time * 90))) * 90
            self.text = Fonts.get_font("Body").render(f"POWER : {round(self.fuel_level * 100)}%", True, "#222222")

        else:
            self.render_time = 0
            self.color = self.color_a.copy()

    def draw(self, surface):
        pygame.draw.rect(surface, (125, 125, 125), self.widget_rect)

        fuel_bar_rect = self.widget_rect.copy()
        fuel_bar_rect.width *= self.fuel_level
        pygame.draw.rect(surface, self.color, fuel_bar_rect)
        color = self.color.copy()
        color[0] *= 0.95
        color[1] *= 0.95
        color[2] *= 0.95
        shade_rect = fuel_bar_rect.copy()
        shade_rect.height /= 2
        shade_rect.y += shade_rect.height 

        pygame.draw.rect(surface, color, shade_rect)

        text_pos = self.widget_rect.copy()
        text_pos.x = self.widget_rect.x + self.widget_size[0] / 2 - self.text.width / 2
        text_pos.y = self.widget_rect.y + self.widget_size[1] / 2 - self.text.height / 2
        surface.blit(self.text, text_pos)

class PlanetInterface:
    def __init__(self):
        self.planet = None
        self.enabled = False
        self.dist = 40
        self.width = 1280 / 3
        self.height = 720 - self.dist * 2
        self.zoom = 1

    def handle_event(self, event):
        pass

    def update(self, camera, delta_time):
        self.planet = camera.selected_planet
        self.zoom = camera.zoom
        self.enabled = self.planet != None

    def draw(self, surface):
        if not self.enabled:
            return
        
        # Draw selected body name
        text = Images.get_image(self.planet.name + " title")
        surface.blit(text, (1280 / 2 - text.get_width() / 2, 720 / 2 - self.planet.radius / self.zoom - 50))
        
        # Draw Mission Board
        pygame.draw.rect(surface, (60, 60, 60), (self.dist, self.dist, self.width, self.height))

        # Render missions
        y_index = 0

        for mission in self.planet.missions:
            mission_image = Images.get_image(mission + " display") 
            surface.blit(mission_image, (self.dist, y_index * mission_image.get_height()))

        # Draw Shop
        pygame.draw.rect(surface, (60, 60, 60), (1280 - self.dist - self.width, self.dist, self.width, self.height))

class Manual:
    def __init__(self):
        self.enabled = False # Keybind T opens manual for tutorial

    def handle_event(self, event):
        pass

    def update(self, delta_time):
        pass

    def draw(self, surface):
        pass

class Log:
    def __init__(self):
        self.enabled = True
        self.active_missions = [] # Keybind J toggles quest log sidebar (active missions) They should also include dist to objective

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_j:
                self.enabled = not self.enabled

    def update(self, delta_time):
        pass

    def draw(self, surface):
        if not self.enabled:
            return

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

    def handle_event(self, event):
        if event.type == MOUSEWHEEL:
            if event.y == 1:
                self.set_zoom(self.zoom + 0.1)

            elif event.y == -1:
                self.set_zoom(self.zoom - 0.1)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.panning = True
                self.last_pos = event.pos

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.panning = False

        elif event.type == KEYDOWN:
            self.key_pressed(event)

    def key_pressed(self, event):
            if event.key == K_UP:
                self.set_zoom(self.zoom + 0.1)

            elif event.key == K_DOWN:
                self.set_zoom(self.zoom - 0.1)

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

    def update(self, entity_manager: EntityManager, player_id:int, planet_ids:list[int], future_player_positions:list[tuple], pirate_handler:PirateHandler):
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
                        pygame.draw.circle(self.map_surface, "#FFFF00", center, calculate_scale(self, planet.dist / 460) + max(calculate_scale(self, planet.radius / 460), 5), 2)
                    else:
                        orbit:Planet = entity_manager.get_component(planet.orbits, Planet)
                        pygame.draw.circle(self.map_surface, "#DDDDDD", center, calculate_scale(self, planet.dist / 460) + calculate_scale(self, planet.radius / 460) + calculate_scale(self, orbit.radius / 460), 2)
            
            #pass two drawing moon orbit
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                if planet.kind == "moon":
                    orbit:Planet = entity_manager.get_component(planet.orbits, Planet)
                    center = calculate_on_map_position(self, pygame.Vector2(orbit.x, orbit.y)) - offset
                    pygame.draw.circle(self.map_surface, "#DDDDDD", center, calculate_scale(self, planet.dist / 460) + calculate_scale(self, planet.radius / 460) + calculate_scale(self, orbit.radius / 460), 2)
            
            #pass three to draw planet positions

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                on_map_position = calculate_on_map_position(self, pygame.Vector2(planet.x, planet.y))

                if planet.kind == "moon":
                    pygame.draw.circle(self.map_surface, "#8923f7", on_map_position - offset, max(calculate_scale(self, planet.radius / 460), 2))

                elif planet.kind == "sun":
                    pygame.draw.circle(self.map_surface, "#ffe354", on_map_position - offset, max(calculate_scale(self, planet.radius / 50), 3))

                else:
                    pygame.draw.circle(self.map_surface, "#2c5fb0", on_map_position - offset, max(calculate_scale(self, planet.radius / 460), 5))

            position:Position = entity_manager.get_component(player_id, Position)

            on_map_position = (self.map_surface_center[0] + calculate_scale(self, position.x / 460), self.map_surface_center[1] + calculate_scale(self, position.y / 460))

            pygame.draw.circle(self.map_surface, "#00FF00", on_map_position  - offset, min(max(calculate_scale(self, 4), 4), 4))

        elif self.map_mode == 2:
            player_position:Position = entity_manager.get_component(player_id, Position)

            # Draw bodies
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                on_map_position = (self.map_surface_center[0] + calculate_scale(self, (planet.x - player_position.x) / 4), self.map_surface_center[1] + calculate_scale(self, (planet.y - player_position.y) / 4))

                if planet.kind == "moon":
                    pygame.draw.circle(self.map_surface, "#8923f7", on_map_position, calculate_scale(self, planet.radius / 4))

                elif planet.kind == "sun":
                    pygame.draw.circle(self.map_surface, "#ffe354", on_map_position, calculate_scale(self, planet.radius / 4))

                else:
                    pygame.draw.circle(self.map_surface, "#2c5fb0", on_map_position, calculate_scale(self, planet.radius / 4))

            # Draw predicted path
            for i in range(len(future_player_positions) - 2):
                p1 = future_player_positions[i]
                p2 = future_player_positions[i + 1]
                pygame.draw.line(self.map_surface, "#FFFFFF", (self.map_surface_center[0] + calculate_scale(self, (p1[0] - player_position.x) / 4), 
                                                                 self.map_surface_center[1] + calculate_scale(self, (p1[1] - player_position.y) / 4)),
                                                                (self.map_surface_center[0] + calculate_scale(self, (p2[0] - player_position.x) / 4), 
                                                                 self.map_surface_center[1] + calculate_scale(self, (p2[1] - player_position.y) / 4)))

            # Draw player
            pygame.draw.circle(self.map_surface, "#00FF00", self.map_surface_center, min(max(calculate_scale(self, 5), 5), 10))

            # Draw pirates
            for entity_id in pirate_handler.pirate_ids:
                pirate_position:Position = entity_manager.get_component(entity_id, Position)
                position = (self.map_surface_center[0] + calculate_scale(self, (pirate_position.x - player_position.x) / 4), self.map_surface_center[1] + calculate_scale(self, (pirate_position.y - player_position.y) / 4))
                pygame.draw.circle(self.map_surface, "#FF0000", position, min(max(calculate_scale(self, 5), 5), 10))

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
        surface.blit(display_surface, (surface.get_width() - display_surface.get_width(), 0))

    def draw_fullscreen(self, surface: pygame.Surface):
        display_surface = pygame.transform.smoothscale(self.map_surface, (1280, 720))
        surface.blit(display_surface, display_surface.get_rect(center = (surface.get_width() - 1280 / 2, 720 / 2)))
