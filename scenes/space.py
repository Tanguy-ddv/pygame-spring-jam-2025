# Built-ins
import json
import math
from typing import Any

# External
import pygame
from pygame.locals import *

# Internal
from pygamelib import *
from entities import *
from assets import Images

class HUD:
    def __init__(self):
        self.map_surface = pygame.Surface((526, 526), pygame.SRCALPHA)
        self.map_surface_center = (526/2, 526/2)

        self.map_mode = 1

    def update(self, entity_manager: EntityManager, player_id:int, planet_ids:list[int]):
        self.map_surface.fill((50, 50, 50))

        if self.map_mode == 1:
            #pass one to draw orbit tracks

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                if planet.kind != "moon":
                    pygame.draw.circle(self.map_surface, (235, 222, 52), self.map_surface_center, planet.dist / 8000, 2)
            
            #pass two to draw planet positions

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                if planet.kind != "moon":
                    on_map_position = (self.map_surface_center[0] + (planet.x / 8000), self.map_surface_center[1] + (planet.y / 8000))

                    pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position, 2)

            position:Position = entity_manager.get_component(player_id, Position)

            on_map_position = (self.map_surface_center[0] + (position.x / 8000), self.map_surface_center[1] + (position.y / 8000))

            pygame.draw.circle(self.map_surface, (0, 0, 255), on_map_position, 3)

        elif self.map_mode == 2:
            player_position:Position = entity_manager.get_component(player_id, Position)

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                on_map_position = (self.map_surface_center[0] + ((planet.x - player_position.x) / 16), self.map_surface_center[1] + ((planet.y - player_position.y) / 16))

                pygame.draw.circle(self.map_surface, (255, 0, 0), on_map_position, planet.radius / 16)

            pygame.draw.circle(self.map_surface, (0, 0, 255), self.map_surface_center, 3)

    def draw(self, surface: pygame.Surface):
        if self.map_mode != 0:
            surface.blit(self.map_surface, self.map_surface.get_rect(center = (surface.get_width() - self.map_surface_center[0], self.map_surface_center[1])))

def open_planets(entity_manager: EntityManager):
    with open("data/celestial_bodies.json") as f:
        planet_dict: dict[str, dict[str, Any]] = json.load(f)
    planet_ids: list[int] = []
    planets: list[Planet] = []
    for name, values in planet_dict.items():
        year = values['year']
        day = values['day']
        dist = values['dist']
        radius = values['radius']
        image_name = values['image_name']
        orbits_str = values['orbits']
        kind = values["kind"]
        mass = values["mass"]
        if orbits_str is None:
            orbits = None
        else:
            for i in range(len(planets)):
                if planets[i].name == orbits_str:
                    orbits = planet_ids[i]

        planet = Planet(name, Images.get_image(image_name), radius, day, year, kind, dist, mass, orbits)

        id = create_entity(entity_manager,
                           planet
                           )
        planet_ids.append(id)
        planets.append(planet)

    return planet_ids
        
class Space(scene.Scene):
    def __init__(self):
        # Entity manager
        self.entity_manager = EntityManager()

        # Systems
        self.background_system = BackgroundSystem()
        self.physics_system = PhysicsSystem()
        self.planet_handler = PlanetHandler()
        self.bloom_system = BloomSystem()
        self.timing_system = TimingSystem()
        self.camera = CameraSystem((1280, 720), (640, 360))

        # Planets
        self.planet_ids = open_planets(self.entity_manager)


        # Player
        starting_planet = self.entity_manager.get_component(self.planet_ids[3], Planet) # Change the planet index to change starting planet NOTE: This sets player pos to centre of planet

        self.player_id = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.player_id, Position(starting_planet.dist * math.cos(math.radians(starting_planet.theta)), starting_planet.dist * math.sin(math.radians(starting_planet.theta))))
        self.entity_manager.add_component(self.player_id, Velocity(0, 0))
        self.entity_manager.add_component(self.player_id, Force(0, 0))
        self.entity_manager.add_component(self.player_id, Mass(20))
        self.entity_manager.add_component(self.player_id, Rotation(0))

        # Player surface
        self.entity_manager.add_component(self.player_id, Images.get_image("player"))

        # Variables
        self.held_keys = set()

        # HUD
        self.hud = HUD()

    def start(self) -> None:
        pass

    def handle_events(self, events: list[pygame.Event]) -> None:
        for event in events:
            if event.type == KEYDOWN:
                self.key_pressed(event)

            elif event.type == KEYUP:
                self.key_unpressed(event)
    
    def handle_held_keys(self, delta_time: float) -> None:
        for key in self.held_keys:
            # Get player attributes
            force = self.entity_manager.get_component(self.player_id, Force)
            rotation = self.entity_manager.get_component(self.player_id, Rotation)

            # Apply thruster force
            if key == K_SPACE:
                force.x += 1500 * math.cos(math.radians(rotation.angle))
                force.y -= 1500 * math.sin(math.radians(rotation.angle))
            
            # Rotate spaceship ACW
            elif key == K_a:
                rotation.angle = (rotation.angle + (120 * delta_time)) % 360
                self.entity_manager.add_component(self.player_id, pygame.transform.rotate(Images.get_image("player"), rotation.angle))

            # Rotate spaceship CW
            elif key == K_d:
                rotation.angle = (rotation.angle - (120 * delta_time)) % 360
                self.entity_manager.add_component(self.player_id, pygame.transform.rotate(Images.get_image("player"), rotation.angle))

            elif key == K_r:
                self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[3], Planet).x - 400, self.entity_manager.get_component(self.planet_ids[3], Planet).y

            elif key == K_1:
                self.hud.map_mode = 1
            elif key == K_2:
                self.hud.map_mode = 2
            elif key == K_0:
                self.hud.map_mode = 0

    def key_pressed(self, event: pygame.Event) -> None:
        self.held_keys.add(event.key)

    def key_unpressed(self, event: pygame.Event) -> None:
        self.held_keys.remove(event.key)

    def update(self, delta_time: float) -> None:
        # Handle input
        self.handle_held_keys(delta_time)

        # Process physics
        self.physics_system.update(self.entity_manager, self.planet_ids, delta_time)

        # Update camera position
        self.camera.set_position(self.entity_manager.get_component(self.player_id, Position))

        # Update stars
        self.background_system.update(self.camera, delta_time)

        # Update planets
        self.planet_handler.update(self.entity_manager, self.camera, delta_time)

        # self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[3], Planet).x, self.entity_manager.get_component(self.planet_ids[3], Planet).y
        
        self.timing_system.update(self.entity_manager, delta_time)

        self.hud.update(self.entity_manager, self.player_id, self.planet_ids)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))

        self.background_system.draw(surface, self.camera, Images)
        self.planet_handler.draw(self.entity_manager, self.camera, surface)
        self.camera.draw(surface, self.entity_manager)
        self.bloom_system.draw(self.camera, surface, self.entity_manager)
        self.hud.draw(surface)

    def stop(self) -> None:
        pass