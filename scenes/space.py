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

        # Player
        self.player_id = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.player_id, Position(0, 1200))
        self.entity_manager.add_component(self.player_id, Velocity(0, 0))
        self.entity_manager.add_component(self.player_id, Force(0, 0))
        self.entity_manager.add_component(self.player_id, Mass(1))
        self.entity_manager.add_component(self.player_id, Rotation(0))

        # Player surface
        self.entity_manager.add_component(self.player_id, Images.get_image("player"))

        # Planets
        self.planet_ids = open_planets(self.entity_manager)

        # Variables
        self.held_keys = set()

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
                force.x += 25 * math.cos(math.radians(rotation.angle))
                force.y -= 25 * math.sin(math.radians(rotation.angle))
            
            # Rotate spaceship ACW
            elif key == K_a:
                rotation.angle = (rotation.angle + (120 * delta_time)) % 360
                self.entity_manager.add_component(self.player_id, pygame.transform.rotate(Images.get_image("player"), rotation.angle))

            # Rotate spaceship CW
            elif key == K_d:
                rotation.angle = (rotation.angle - (120 * delta_time)) % 360
                self.entity_manager.add_component(self.player_id, pygame.transform.rotate(Images.get_image("player"), rotation.angle))

            # elif key == K_1:
                # self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[3], Planet).x + 800, self.entity_manager.get_component(self.planet_ids[3], Planet).y

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

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))

        self.background_system.draw(surface, self.camera, Images)
        self.planet_handler.draw(self.entity_manager, self.camera, surface)
        self.camera.draw(surface, self.entity_manager)
        self.bloom_system.draw(self.camera, surface, self.entity_manager)

    def stop(self) -> None:
        pass