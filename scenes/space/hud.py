# Built-ins

# External
import pygame
import math
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *
from utils.constants import GAMEH_PER_REALSEC

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

        future_player_positions, future_player_crash = self.simulate(entity_manager, player_id, planet_imprints, 200)

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

            player_position:Position = entity_manager.get_component(player_id, Position)

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                on_map_position = (self.map_surface_center[0] + calculate_scale(self, (planet.x - player_position.x) / 4), self.map_surface_center[1] + calculate_scale(self, (planet.y - player_position.y) / 4))

                pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position, calculate_scale(self, planet.radius / 4))

            for i in range(len(future_player_positions) - 2):
                p1 = future_player_positions[i]
                p2 = future_player_positions[i + 1]
                pygame.draw.line(self.map_surface, (0, 255, 0), (self.map_surface_center[0] + calculate_scale(self, (p1[0] - player_position.x) / 4), 
                                                                 self.map_surface_center[1] + calculate_scale(self, (p1[1] - player_position.y) / 4)),
                                                                (self.map_surface_center[0] + calculate_scale(self, (p2[0] - player_position.x) / 4), 
                                                                 self.map_surface_center[1] + calculate_scale(self, (p2[1] - player_position.y) / 4)))
            
            if future_player_crash:
                size = max(min(calculate_scale(self, 20), 40), 10)
                surface = pygame.Surface((size,size), pygame.SRCALPHA)
                pygame.draw.line(surface, (235, 222, 52), (0, 0), (size, size), 4)
                pygame.draw.line(surface, (235, 222, 52), (size, 0), (0, size), 4)
                position = (self.map_surface_center[0] + calculate_scale(self, (future_player_positions[len(future_player_positions) - 1][0] - player_position.x) / 4), 
                            self.map_surface_center[1] + calculate_scale(self, (future_player_positions[len(future_player_positions) - 1][1] - player_position.y) / 4))
                self.map_surface.blit(surface, surface.get_rect(center = position))

            pygame.draw.circle(self.map_surface, (0, 0, 255), self.map_surface_center, 5)

    def simulate(self, entity_manager:EntityManager, player_id:int, planet_imprints:dict[int:PlanetImprint], i:int):
        player_position = Position(entity_manager.get_component(player_id, Position).xy)
        player_velocity = Velocity(entity_manager.get_component(player_id, Velocity).xy)
        player_force= Force(entity_manager.get_component(player_id, Force).xy)
        player_mass = Mass(entity_manager.get_component(player_id, Mass).get_mass())

        future_player_positions = [player_position.xy]

        dt = 0.05

        j = 0

        crash = False

        while j < i and crash == False:
            self.update_planet_imprints(planet_imprints, dt)
            for planet_id in planet_imprints:
                planet = planet_imprints[planet_id]
                distance = max(math.sqrt((planet.x - player_position.x)** 2 + (planet.y - player_position.y)**2), 1)

                if distance < planet.radius:
                    crash = True
            
            if crash == False:
                for planet_id in planet_imprints:
                    planet = planet_imprints[planet_id]
                    distance = max(math.sqrt((planet.x - player_position.x)** 2 + (planet.y - player_position.y)**2), 1)
                    if planet.kind == "moon":
                        continue # skip moons due to difficulty orbiting planets (n-body problem)

                    direction = math.atan2((planet.y - player_position.y), (planet.x - player_position.x))

                    player_force.x += 9.81 * math.cos(direction) * (player_mass.magnitude * planet.mass) / distance
                    player_force.y += 9.81 * math.sin(direction) * (player_mass.magnitude * planet.mass) / distance
                
                # Update motion
                player_velocity += player_force / player_mass.get_mass() * dt
                player_position += player_velocity * dt

                # Reset force each frame
                player_force.xy = (0, 0)

                future_player_positions.append(player_position.xy)

            j += 1
        
        return future_player_positions, crash
    
    def update_planet_imprints(self, planet_imprints:dict[int:PlanetImprint], delta_time: float):
        for planet_id, planet_imprint in planet_imprints.items():
            planet_imprint:PlanetImprint
            if planet_imprint.orbits is not None:
                planet_imprint.theta = (delta_time/planet_imprint.year*24*GAMEH_PER_REALSEC + planet_imprint.theta)%360

                orbit:PlanetImprint = planet_imprints[planet_imprint.orbits]

                planet_imprint.x, planet_imprint.y = orbit.x + (planet_imprint.dist + orbit.radius + planet_imprint.radius)*math.cos(planet_imprint.theta*math.pi/180), orbit.y + (planet_imprint.dist + orbit.radius + planet_imprint.radius)*math.sin(planet_imprint.theta*math.pi/180)

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