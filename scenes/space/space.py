# Built-ins
import pygame
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
from utils import *
from ..space.hud import HUD

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
                           planet,
                           CircleCollider((0, 0), math.floor(math.sqrt(radius)), False)
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
        self.health_system = HealthSystem()
        self.collision_system = CollisionsSystem()
        self.simulator = SimulationSystem()
        self.bullet_system = BulletSystem()
        self.shield_renderer = ShieldRenderer()
        self.pirate_handler = PirateHandler()

        # Planets
        self.planet_ids = open_planets(self.entity_manager)

        # Player
        self.starting_planet = self.entity_manager.get_component(self.planet_ids[3], Planet) # Please dont change this from now its set to earth for tutorial reasons later on

        self.player_id = create_entity(self.entity_manager,
                                       Images.get_image("shuttle"),
                                       Rotation(0),
                                       Health(1, 5000),
                                       Fuel(1000, 1000),
                                       Animator(),
                                       Position(self.starting_planet.dist * math.cos(math.radians(self.starting_planet.theta)) + self.starting_planet.radius * 3, self.starting_planet.dist * math.sin(math.radians(self.starting_planet.theta))),
                                       Velocity(0, 0),
                                       Force(0, 0),
                                       Mass(20),
                                       CircleCollider((0, 0), 9),
                                       OtherIds(),
                                       Shield(),
                                       Simulate() # This makes player affected by physics
                                       ) 

        # Variables
        self.held_keys = set()

        # HUD
        self.hud = HUD()

    def start(self) -> None:
        sound:pygame.Sound = Sounds.get_sound("bgm")
        sound.set_volume(0.5)
        sound.play(-1)

    def handle_events(self, events: list[pygame.Event]) -> None:
        if self.entity_manager.has_component(self.player_id, Dying):
            return
        
        for event in events:
            if event.type == KEYDOWN:
                self.key_pressed(event)

            elif event.type == KEYUP:
                self.key_unpressed(event)

            elif event.type in [MOUSEWHEEL, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                self.hud.handle_event(event)
                self.planet_handler.handle_event(self.entity_manager, self.camera, event)

    def handle_held_keys(self, delta_time: float) -> None:
        if self.entity_manager.has_component(self.player_id, Dying):
            return
        
        for key in self.held_keys:
            # Get player attributes
            position:Position = self.entity_manager.get_component(self.player_id, Position)
            velocity:Velocity = self.entity_manager.get_component(self.player_id, Velocity)
            force:Force = self.entity_manager.get_component(self.player_id, Force)
            rotation:Rotation = self.entity_manager.get_component(self.player_id, Rotation)
            animator:Animator = self.entity_manager.get_component(self.player_id, Animator)

            # Apply thruster force
            if key == K_w:
                fuel = self.entity_manager.get_component(self.player_id, Fuel)
                if not fuel.fuel:
                    continue

                fuel.consume(THRUSTER_FUEL_RATE * delta_time)
                force.x += 1500 * math.cos(math.radians(rotation.angle))
                force.y -= 1500 * math.sin(math.radians(rotation.angle))

                if  "main drive start" in animator.animation_stack and round(animator.animation_stack["main drive start"]) >= 5:
                    animator.animation_stack["main drive hold"] =  0
                    animator.animation_stack.pop("main drive start")

            # Rotate spaceship ACW
            elif key == K_a:
                rotation.angle = (rotation.angle + (120 * delta_time)) % 360

                if  "spin aclockwise start" in animator.animation_stack and round(animator.animation_stack["spin aclockwise start"]) >= 4:
                    animator.animation_stack["spin aclockwise hold"] =  0
                    animator.animation_stack.pop("spin aclockwise start")

            # Rotate spaceship CW
            elif key == K_d:
                rotation.angle = (rotation.angle - (120 * delta_time)) % 360

                if  "spin clockwise start" in animator.animation_stack and round(animator.animation_stack["spin clockwise start"]) >= 4:
                    animator.animation_stack["spin clockwise hold"] =  0
                    animator.animation_stack.pop("spin clockwise start")
            
            elif key == K_t:
                self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[17], Planet).x + 800, self.entity_manager.get_component(self.planet_ids[17], Planet).y

    def key_pressed(self, event: pygame.Event) -> None:
        position = self.entity_manager.get_component(self.player_id, Position)
        velocity = self.entity_manager.get_component(self.player_id, Velocity)
        rotation = self.entity_manager.get_component(self.player_id, Rotation)
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        shield:Shield = self.entity_manager.get_component(self.player_id, Shield)
        health:Health = self.entity_manager.get_component(self.player_id, Health)
        circle:CircleCollider = self.entity_manager.get_component(self.player_id, CircleCollider)

        if event.key == K_a:
            animator.animation_stack["spin clockwise start"] = 0

        elif event.key == K_d:
            animator.animation_stack["spin aclockwise start"] = 0

        elif event.key == K_w:
            animator.animation_stack["main drive start"] = 0
            Sounds.get_sound("thrusters").play(loops=-1)

        elif event.key == K_SPACE and not shield.activated:
            id = create_entity(self.entity_manager, 
                               Position(position.x + 0 * math.cos(math.radians(rotation.angle)), position.y - 0 * math.sin(math.radians(rotation.angle))),
                               Velocity(0, 0),
                               Mass(0.00001),
                               Force(3 * math.cos(math.radians(rotation.angle)), -3 * math.sin(math.radians(rotation.angle))),
                               pygame.transform.rotate(Images.get_image("laser"), rotation.angle),
                               Timer(),
                               Bullet(rotation.angle),
                               CircleCollider((position.x, position.y), 2),
                               OriginId(self.player_id),
                               Simulate() # This is needed for all entities using the physics system
                               )
            
            self.entity_manager.get_component(self.player_id, OtherIds).add_other_id(id)
        
        elif event.key == K_s:
            circle.radius = 32.5
            shield.up()

        self.held_keys.add(event.key)
        self.hud.handle_event(event)

    def key_unpressed(self, event: pygame.Event) -> None:
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        shield:Shield = self.entity_manager.get_component(self.player_id, Shield)
        health:Health = self.entity_manager.get_component(self.player_id, Health)
        circle:CircleCollider = self.entity_manager.get_component(self.player_id, CircleCollider)

        if event.key == K_a:
            for animation in ["spin clockwise start", "spin clockwise hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        elif event.key == K_d:
            for animation in ["spin aclockwise start", "spin aclockwise hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        elif event.key == K_w:
            for animation in ["main drive start", "main drive hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)
                    Sounds.get_sound("thrusters").stop()

        elif event.key == K_s:
            circle.radius = 9
            shield.down()

        if event.key in self.held_keys:
            self.held_keys.remove(event.key)

    def update(self, delta_time: float) -> None:
        # Update camera position
        self.camera.update(self.entity_manager, self.player_id, delta_time)

        if self.camera.selected_planet != None and self.camera.changed:
            self.background_system.reset_stars(self.camera)
            self.camera.changed = False
            
        # Simulate death
        health:Health = self.entity_manager.get_component(self.player_id, Health)
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        other_ids:OtherIds = self.entity_manager.get_component(self.player_id, OtherIds)
        shield:Shield = self.entity_manager.get_component(self.player_id, Shield)

        if self.entity_manager.has_component(self.player_id, Collided):
            for id in self.entity_manager.get_component(self.player_id, Collided).other:
                if id in self.planet_ids:
                    health.health = -1000
                else:
                    if not other_ids.check_for_other_id(id) and shield.activated == False:
                        health.take_damage(1)

            self.entity_manager.remove_component(self.player_id, Collided)

        if health.health <= 0:
            if not self.entity_manager.has_component(self.player_id, Dying):
                self.entity_manager.add_component(self.player_id, Dying())
                animator.animation_stack = {"explosion1": 0}
        
        if self.entity_manager.has_component(self.player_id, Dying):
            if round(animator.animation_stack["explosion1"]) >= 18:
                # Stop dying
                self.entity_manager.remove_component(self.player_id, Dying)
                animator.animation_stack.pop("explosion1")

                # Respawn / code on death VVVVVVVV
                self.entity_manager.add_component(self.player_id, Position(self.starting_planet.dist * math.cos(math.radians(self.starting_planet.theta)) + self.starting_planet.radius * 3, self.starting_planet.dist * math.sin(math.radians(self.starting_planet.theta))))
                self.entity_manager.add_component(self.player_id, Velocity(0, 0))
                self.entity_manager.add_component(self.player_id, Force(0, 0))
                self.entity_manager.add_component(self.player_id, Health(1, 1000))
                self.held_keys.clear()
                Sounds.get_sound("thrusters").stop()

        # Handle input
        self.handle_held_keys(delta_time)
        
        # Update player surface
        player_rotation = self.entity_manager.get_component(self.player_id, Rotation)
        player_position:Position = self.entity_manager.get_component(self.player_id, Position) 
        player_circle:CircleCollider = self.entity_manager.get_component(self.player_id, CircleCollider) 
        player_circle.x, player_circle.y = player_position.x, player_position.y
        self.entity_manager.add_component(self.player_id, pygame.transform.rotate(Images.get_image("shuttle"), player_rotation.angle - 90))

        # Update animations
        self.animation_system.update(self.entity_manager, delta_time)

        # updated the simulator
        self.simulator.simulate(self.entity_manager, [self.player_id], self.planet_handler.get_planet_imprints(self.entity_manager), 50)

        # Process physics
        self.physics_system.update(self.entity_manager, self.planet_ids, delta_time)

        # Update stars
        self.background_system.update(self.camera, delta_time)

        # Update planets
        self.planet_handler.update(self.entity_manager, self.camera, delta_time)
        self.bullet_system.update(self.entity_manager)
        self.pirate_handler.update(self.entity_manager)

        # self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[3], Planet).x, self.entity_manager.get_component(self.planet_ids[3], Planet).y
        
        self.timing_system.update(self.entity_manager, delta_time)
        self.health_system.update(self.entity_manager, delta_time)
        self.collision_system.update(self.entity_manager)
        
        simulated_player = self.simulator.get_simulated_entity(self.player_id)
        self.hud.update(self.entity_manager, self.player_id, self.planet_ids, simulated_player["future_positions"], simulated_player["crash"], self.camera, delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        self.camera.get_surface().fill((0, 0, 0))
        
        if not self.hud.map.fullscreened or self.hud.map.map_mode == 0: # Render when not fullscreened or when toggled off
            self.background_system.draw(self.camera.get_surface(), self.camera, Images)
            self.planet_handler.draw(self.entity_manager, self.camera, self.camera.get_surface())
            self.camera.draw(self.entity_manager)
            self.animation_system.draw(self.camera.get_surface(), self.entity_manager, self.camera)
            self.bloom_system.draw(self.camera, self.camera.get_surface(), self.entity_manager)
            self.shield_renderer.draw(self.entity_manager, self.camera)
            if self.camera.zoom == 1:
                surface.blit(self.camera.get_surface())
            else:
                surface.blit(pygame.transform.smoothscale(self.camera.get_surface(), self.camera.screen_size))

        self.hud.draw(surface)

    def stop(self) -> None:
        Sounds.get_sound("bgm").stop()

"""
TODO:

- Someone needs to add functionality for multiple animations playing simultaneously 
e.g. main drive + spin

- Missions

- Pirates

- Some feedback loop to encourage player

- New assets for all planets + bodies (Yaroslav)

- Visual update for the background as opposed to all black fill + stars

"""