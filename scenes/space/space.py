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
from assets import *
from .hud import HUD

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
        rotation_direction = values["rotation_direction"]
        if orbits_str is None:
            orbits = None
        else:
            for i in range(len(planets)):
                if planets[i].name == orbits_str:
                    orbits = planet_ids[i]

        planet = Planet(name, Images.get_image(image_name), radius, day, year, kind, dist, mass, orbits, rotation_direction)

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
        self.animation_system = AnimationSystem()

        # Planets
        self.planet_ids = open_planets(self.entity_manager)

        # Player
        starting_planet = self.entity_manager.get_component(self.planet_ids[7], Planet) # Change the planet index to change starting planet

        self.player_id = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.player_id, Position(starting_planet.dist * math.cos(math.radians(starting_planet.theta)) + starting_planet.radius * 3, starting_planet.dist * math.sin(math.radians(starting_planet.theta))))
        self.entity_manager.add_component(self.player_id, Velocity(0, 0))
        self.entity_manager.add_component(self.player_id, Force(0, 0))
        self.entity_manager.add_component(self.player_id, Mass(20))
        self.entity_manager.add_component(self.player_id, Rotation(0))
        self.entity_manager.add_component(self.player_id, Animator())

        # Player surface
        self.entity_manager.add_component(self.player_id, Images.get_image("shuttle"))

        # Variables
        self.held_keys = set()

        # HUD
        self.hud = HUD()

    def start(self) -> None:
        sound:pygame.Sound = Sounds.get_sound("bgm")
        sound.set_volume(0.5)
        sound.play(-1)

    def handle_events(self, events: list[pygame.Event]) -> None:
        for event in events:
            if event.type == KEYDOWN:
                self.key_pressed(event)

            elif event.type == KEYUP:
                self.key_unpressed(event)

            elif event.type in [MOUSEWHEEL, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                self.hud.handle_event(event)

    def handle_held_keys(self, delta_time: float) -> None:
        for key in self.held_keys:
            # Get player attributes
            force = self.entity_manager.get_component(self.player_id, Force)
            rotation = self.entity_manager.get_component(self.player_id, Rotation)
            animator = self.entity_manager.get_component(self.player_id, Animator)

            # Apply thruster force
            if key == K_SPACE:
                force.x += 1500 * math.cos(math.radians(rotation.angle))
                force.y -= 1500 * math.sin(math.radians(rotation.angle))

                if  "main drive start" in animator.animation_stack and animator.animation_stack["main drive start"] > 5:
                    animator.animation_stack["main drive hold"] =  0
                    animator.animation_stack.pop("main drive start")

            # Rotate spaceship ACW
            elif key == K_a:
                rotation.angle = (rotation.angle + (120 * delta_time)) % 360

                if  "spin aclockwise start" in animator.animation_stack and animator.animation_stack["spin aclockwise start"] > 4:
                    animator.animation_stack["spin aclockwise hold"] =  0
                    animator.animation_stack.pop("spin aclockwise start")

            # Rotate spaceship CW
            elif key == K_d:
                rotation.angle = (rotation.angle - (120 * delta_time)) % 360

                if  "spin clockwise start" in animator.animation_stack and animator.animation_stack["spin clockwise start"] > 4:
                    animator.animation_stack["spin clockwise hold"] =  0
                    animator.animation_stack.pop("spin clockwise start")

            elif key == K_t:
                self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[17], Planet).x + 800, self.entity_manager.get_component(self.planet_ids[17], Planet).y

    def key_pressed(self, event: pygame.Event) -> None:
        animator = self.entity_manager.get_component(self.player_id, Animator)
        if event.key == K_a:
            animator.animation_stack["spin clockwise start"] = 0

        elif event.key == K_d:
            animator.animation_stack["spin aclockwise start"] = 0

        elif event.key == K_SPACE:
            animator.animation_stack["main drive start"] = 0

        self.held_keys.add(event.key)
        self.hud.handle_event(event)

    def key_unpressed(self, event: pygame.Event) -> None:
        animator = self.entity_manager.get_component(self.player_id, Animator)
        if event.key == K_a:
            for animation in ["spin clockwise start", "spin clockwise hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        elif event.key == K_d:
            for animation in ["spin aclockwise start", "spin aclockwise hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        elif event.key == K_SPACE:
            for animation in ["main drive start", "main drive hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        self.held_keys.remove(event.key)

    def update(self, delta_time: float) -> None:
        # Handle input
        self.handle_held_keys(delta_time)
        
        # Update player surface
        player_rotation = self.entity_manager.get_component(self.player_id, Rotation)
        self.entity_manager.add_component(self.player_id, pygame.transform.rotate(Images.get_image("shuttle"), player_rotation.angle - 90))

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
        self.hud.update(self.entity_manager, self.player_id, self.planet_ids, self.planet_handler.get_planet_imprints(self.entity_manager), delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))

        if not self.hud.map.fullscreened or self.hud.map.map_mode == 0: # Render when not fullscreened or when toggled off
            self.background_system.draw(surface, self.camera, Images)
            self.planet_handler.draw(self.entity_manager, self.camera, surface)
            self.camera.draw(surface, self.entity_manager)
            self.animation_system.draw(surface, self.entity_manager, self.camera)
            self.bloom_system.draw(self.camera, surface, self.entity_manager)

        if self.hud.map.map_mode != 0:
            self.hud.draw(surface)

    def stop(self) -> None:
        Sounds.get_sound("bgm").stop()

"""
TODO:

- Someone needs to add functionality for multiple animations playing simultaneously 
e.g. main drive + spin

- Fuel system (Nott)
- Weapons? (Nott)

- Missions

- Pirates

- Some feedback loop to encourage player

- New assets for all planets + bodies (Yaroslav)

- Visual update for the background as opposed to all black fill + stars

"""