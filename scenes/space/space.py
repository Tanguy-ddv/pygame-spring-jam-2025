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
from .spawning import find_spawn_chunks_for_planet, spawn_planet_siege

MAX_RADIANS = math.pi * 2

def get_shortest_distance_in_radians(radians_1:int|float, radians_2:int|float):
    difference = (radians_2 - radians_1) % MAX_RADIANS
    return 2 * difference % MAX_RADIANS - difference


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
                           CircleCollider((0, 0), math.floor(math.sqrt(radius)), False),
                           )
        planet_ids.append(id)
        planets.append(planet)

        if kind == "sun":
            entity_manager.add_component(id, Waypoint(pygame.Vector2(0, 0), 5000, (255, 227, 84)))
        elif kind == "moon":
            entity_manager.add_component(id, Waypoint(pygame.Vector2(0, 0), 2560, (137, 35, 247)))
        else:
            entity_manager.add_component(id, Waypoint(pygame.Vector2(0, 0), 2560, (44, 95, 176)))

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
        self.pirate_handler = PirateHandler()

        # Planets
        self.planet_ids = open_planets(self.entity_manager)
        self.planet_dict = {self.entity_manager.get_component(planet_id, Planet).name: planet_id for planet_id in self.planet_ids}

        # Player
        self.starting_planet = self.entity_manager.get_component(self.planet_dict["earth"], Planet) # Please dont change this from now its set to earth for tutorial reasons later on
        self.starting_planet_orbits = self.entity_manager.get_component(self.starting_planet.orbits, Planet)
        self.playing = True
        self.gameover = False
        self.restart = False
        self.transition_timer = None
        self.bullet_timer = 0
        self.spawn_time = 0

        spawn_chunks = find_spawn_chunks_for_planet(self.entity_manager, self.planet_ids, self.planet_dict["earth"], 30)
        spawn_chunk = 15
        while spawn_chunks[spawn_chunk] != False:
            spawn_chunk = random.randint(0, 11) * 30 + 15
        spawn_chunks[spawn_chunk] = True

        dist = (self.starting_planet.dist + self.starting_planet.radius + self.starting_planet_orbits.radius)
        spawn_position = (dist * math.cos(math.radians(self.starting_planet.theta))), dist * math.sin(math.radians(self.starting_planet.theta))
        spawn_position = (spawn_position[0] + math.cos(math.radians(spawn_chunk)) * self.starting_planet.diameter * 5, spawn_position[1] + math.sin(math.radians(spawn_chunk)) * self.starting_planet.diameter * 5)

        self.player_id = create_entity(self.entity_manager,
                                       Images.get_image("shuttle"),
                                       Rotation(0),
                                       Health(1, 1000),
                                       Fuel(1000, 1000),
                                       Balance(0),
                                       Animator(),
                                       Position(spawn_position),
                                       Velocity(0, 0),
                                       Force(0, 0),
                                       Mass(20),
                                       CircleCollider((0, 0), 9),
                                       OtherIds(),
                                       Simulate() # This makes player affected by physics
                                       )
        
        # Variables
        self.held_keys = set()
        self.prompt_colour = [0, 0, 0]
        self.time_elapsed = 0
        self.duration = .5

        # HUD
        self.hud = HUD(
            self.entity_manager.get_component(self.player_id, Fuel),
            self.entity_manager.get_component(self.player_id, Balance)
        )

    def start(self) -> None:
        sound:pygame.mixer.Sound = Sounds.get_sound("bgm")
        sound.set_volume(0.5)
        sound.play(-1)

    def handle_events(self, events: list[pygame.event.Event], delta_time: float) -> None:
        if self.entity_manager.has_component(self.player_id, Dying):
            return
        
        for event in events:
            if event.type == KEYDOWN:
                self.key_pressed(event, delta_time)

            elif event.type == KEYUP:
                self.key_unpressed(event)

            elif event.type in [MOUSEWHEEL, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                if self.gameover:
                    if self.transition_timer == None:
                        Sounds.get_sound("select").play()
                        self.transition_timer = Sounds.get_sound("select").get_length()
                    
                    return
                
                self.hud.handle_event(self.camera, event)

    def handle_held_keys(self, delta_time: float) -> None:
        if self.entity_manager.has_component(self.player_id, Dying):
            return
        
        # Get player attributes
        position:Position = self.entity_manager.get_component(self.player_id, Position)
        velocity:Velocity = self.entity_manager.get_component(self.player_id, Velocity)
        force:Force = self.entity_manager.get_component(self.player_id, Force)
        rotation:Rotation = self.entity_manager.get_component(self.player_id, Rotation)
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        fuel = self.entity_manager.get_component(self.player_id, Fuel)

        for key in self.held_keys:
            # Apply thruster force
            if key == K_w:
                if not fuel.fuel:
                    for anim in ["main drive start", "main drive hold"]:
                        if anim in animator.animation_stack:
                            animator.animation_stack.pop(anim)
                    
                    Sounds.get_sound("thrusters").fadeout(100)
                    continue

                fuel.consume(THRUSTER_FUEL_RATE * delta_time)
                force.x += 1500 * math.cos(math.radians(rotation.angle))
                force.y -= 1500 * math.sin(math.radians(rotation.angle))

                if  "main drive start" in animator.animation_stack and round(animator.animation_stack["main drive start"]) >= 5:
                    animator.animation_stack["main drive hold"] =  0
                    animator.animation_stack.pop("main drive start")

            # Rotate spaceship ACW
            elif key == K_a:
                rotation.angle = (rotation.angle + (240 * delta_time)) % 360

                if  "spin clockwise start" in animator.animation_stack and round(animator.animation_stack["spin clockwise start"]) >= 4:
                    animator.animation_stack["spin clockwise hold"] =  0
                    animator.animation_stack.pop("spin clockwise start")

            # Rotate spaceship CW
            elif key == K_d:
                rotation.angle = (rotation.angle - (240 * delta_time)) % 360

                if  "spin aclockwise start" in animator.animation_stack and round(animator.animation_stack["spin aclockwise start"]) >= 4:
                    animator.animation_stack["spin aclockwise hold"] =  0
                    animator.animation_stack.pop("spin aclockwise start")

            # Fire bullet
            elif key == K_SPACE and self.bullet_timer <= 0:
                final_direction = rotation.angle
                for pirate_id in self.pirate_handler.pirate_ids:
                    pirate_position:Position = self.entity_manager.get_component(pirate_id, Position)
                    pirate_velocity:Velocity = self.entity_manager.get_component(pirate_id, Velocity)
                    direction = math.atan2((pirate_position.y - position.y), (pirate_position.x - position.x))
                    direction_inaccuracy = math.degrees(get_shortest_distance_in_radians(math.radians(rotation.angle), -direction))
                    if abs(direction_inaccuracy) <= 10:
                        distance = math.sqrt((pirate_position.x - position.x) ** 2 + (pirate_position.y - position.y) ** 2)
                        bullet_distance = distance / (100000 * delta_time)
                        true_pirate_location = (pirate_position.x + (pirate_velocity.x * bullet_distance), pirate_position.y + (pirate_velocity.y * bullet_distance))
                        final_direction = math.degrees(-math.atan2((true_pirate_location[1] - position.y), (true_pirate_location[0] - position.x)))
                        
                radians_final_direction = math.radians(final_direction)
                id = create_bullet(self.entity_manager, (position.x + 20 * math.cos(radians_final_direction), position.y - 20 * math.sin(radians_final_direction)), final_direction, self.player_id)
                self.entity_manager.get_component(self.player_id, OtherIds).add_other_id(id)
                self.bullet_timer = 0.25
                fuel.consume(BULLET_COST)

    def key_pressed(self, event: pygame.event.Event, delta_time: float) -> None:
        position = self.entity_manager.get_component(self.player_id, Position)
        velocity = self.entity_manager.get_component(self.player_id, Velocity)
        rotation = self.entity_manager.get_component(self.player_id, Rotation)
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        health:Health = self.entity_manager.get_component(self.player_id, Health)
        circle:CircleCollider = self.entity_manager.get_component(self.player_id, CircleCollider)
        fuel = self.entity_manager.get_component(self.player_id, Fuel)

        if self.gameover:
            if self.transition_timer == None:
                Sounds.get_sound("select").play()
                self.transition_timer = Sounds.get_sound("select").get_length()
                
            return
        
        if event.key == K_ESCAPE:
                self.playing = not self.playing

        elif not self.playing:
            return
            
        elif event.key == K_a:
            animator.animation_stack["spin aclockwise start"] = 0

        elif event.key == K_d:
            animator.animation_stack["spin clockwise start"] = 0

        elif event.key == K_w:
            animator.animation_stack["main drive start"] = 0
            Sounds.get_sound("thrusters").play(loops=-1, fade_ms=500)

        elif event.key == K_f:
            # Check if docked then undock
            if self.camera.selected_planet != None:
                self.camera.selected_planet = None
                self.camera.changed = True
                return
            
            # Dock at planet
            for planet_id in self.entity_manager.get_from_components(Planet):
                planet: Planet = self.entity_manager.get_component(planet_id, Planet)

                if math.hypot(position.x - planet.x, position.y - planet.y) < 350:
                    self.camera.selected_planet = planet
                    self.camera.changed = True
                    return
                
        elif event.key == K_SPACE and self.bullet_timer <= 0:
            final_direction = rotation.angle
            for pirate_id in self.pirate_handler.pirate_ids:
                pirate_position = self.entity_manager.get_component(pirate_id, Position)
                pirate_velocity = self.entity_manager.get_component(pirate_id, Velocity)
                direction = math.atan2((pirate_position.y - position.y), (pirate_position.x - position.x))
                direction_inaccuracy = math.degrees(get_shortest_distance_in_radians(math.radians(rotation.angle), -direction))
                if abs(direction_inaccuracy) <= 10:
                    distance = math.sqrt((pirate_position.x - position.x) ** 2 + (pirate_position.y - position.y) ** 2)
                    bullet_distance = distance / (100000 * delta_time)
                    true_pirate_location = (pirate_position.x + (pirate_velocity.x * bullet_distance), pirate_position.y + (pirate_velocity.y * bullet_distance))
                    final_direction = math.degrees(-math.atan2((true_pirate_location[1] - position.y), (true_pirate_location[0] - position.x)))
            
            radians_final_direction = math.radians(final_direction)
            id = create_bullet(self.entity_manager, (position.x + 20 * math.cos(radians_final_direction), position.y - 20 * math.sin(radians_final_direction)), final_direction, self.player_id)
            self.entity_manager.get_component(self.player_id, OtherIds).add_other_id(id)
            self.bullet_timer = 0.25
            fuel.consume(BULLET_COST)

        self.held_keys.add(event.key)
        self.hud.handle_event(self.camera, event)

    def key_unpressed(self, event: pygame.event.Event) -> None:
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        health:Health = self.entity_manager.get_component(self.player_id, Health)
        circle:CircleCollider = self.entity_manager.get_component(self.player_id, CircleCollider)

        if event.key == K_a:
            for animation in ["spin aclockwise start", "spin aclockwise hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        elif event.key == K_d:
            for animation in ["spin clockwise start", "spin clockwise hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

        elif event.key == K_w:
            for animation in ["main drive start", "main drive hold"]:
                if animation in animator.animation_stack:
                    animator.animation_stack.pop(animation)

            Sounds.get_sound("thrusters").fadeout(300)

        if event.key in self.held_keys:
            self.held_keys.remove(event.key)

    def update(self, delta_time: float) -> None:
        self.time_elapsed += delta_time
        self.bullet_timer -= delta_time
        self.spawn_time += delta_time

        # Update camera position
        self.camera.update(self.entity_manager, self.player_id, delta_time)

        if self.camera.selected_planet != None and self.camera.changed:
            self.background_system.reset_stars(self.camera)
            self.camera.changed = False
            self.hud.log.last_state = self.hud.log.enabled
            self.hud.log.enabled = True

        elif self.camera.changed:
            self.camera.changed = False
            last = self.hud.log.enabled
            self.hud.log.enabled = self.hud.log.last_state
            self.hud.log.last_state = last
            
        # Simulate death
        health:Health = self.entity_manager.get_component(self.player_id, Health)
        animator:Animator = self.entity_manager.get_component(self.player_id, Animator)
        other_ids:OtherIds = self.entity_manager.get_component(self.player_id, OtherIds)
        fuel:Fuel = self.entity_manager.get_component(self.player_id, Fuel)
        
        if not self.entity_manager.has_component(self.player_id, Dying):
            if self.entity_manager.has_component(self.player_id, Collided):
                for id in self.entity_manager.get_component(self.player_id, Collided).other:
                    if id in self.planet_ids or id in self.pirate_handler.pirate_ids:
                        health.health -= 1000
                    else:
                        if not other_ids.check_for_other_id(id) and health.invincability == 0:
                            fuel.consume(250)
                            health.invincability = health.invincability_window

                self.entity_manager.remove_component(self.player_id, Collided)

        if fuel.fuel <= 0:
            health.health -= 1000

        if health.health <= 0:
            if not self.entity_manager.has_component(self.player_id, Dying) and not self.gameover:
                self.entity_manager.add_component(self.player_id, Dying())
                animator.animation_stack = {"explosion1": 0}
                self.entity_manager.remove_component(self.player_id, Simulate)
        
        if self.entity_manager.has_component(self.player_id, Dying):
            self.entity_manager.remove_component(self.player_id, Simulate)
            if round(animator.animation_stack["explosion1"]) >= 18:
                # Stop dying
                self.entity_manager.remove_component(self.player_id, Dying)
                self.playing = False
                self.gameover = True
                self.time_elapsed = 0

                animator.animation_stack.pop("explosion1")

                # Respawn / code on death VVVVVVVV
                # self.entity_manager.add_component(self.player_id, Position(self.starting_planet.dist * math.cos(math.radians(self.starting_planet.theta)) + self.starting_planet.radius * 3, self.starting_planet.dist * math.sin(math.radians(self.starting_planet.theta))))
                # self.entity_manager.add_component(self.player_id, Velocity(0, 0))
                # self.entity_manager.add_component(self.player_id, Force(0, 0))
                # self.entity_manager.add_component(self.player_id, Health(1, 1000))
                # self.held_keys.clear()

                # Stop all active sounds
                Sounds.get_sound("thrusters").stop()

                # Play gameover sounds
                Sounds.get_sound("lose").play()

        # Spawn pirate based on mission value:
        mission_remove_list = []
        if self.hud.log.mission_dict == {}:
            self.spawn_time = 0

        for mission in self.hud.log.mission_dict:
            if random.randint(0, 1000) < 1 + math.sqrt(mission.reward) and mission.type != "kill" and self.spawn_time >= 50 and self.playing:
                self.spawn_time -= 50
                pos = self.entity_manager.get_component(self.player_id, Position).copy()
                pos.x += random.choice([-1280, 1280])
                pos.y += random.choice([-720, 720])

                pirate_type = random.choice(["pirate", "pirate skull", "pirate smile", "pirate light", "pirate light smile"])
                pirate_id = create_pirate(self.entity_manager, pos, Images.get_image(pirate_type), pirate_type)
                self.pirate_handler.register_pirate(pirate_id)
            
            if mission.type == "delivery":
                if self.camera.selected_planet.name == mission.destination:
                    mission.set_type("complete")

            elif mission.type == "kill":
                for dead_pirate in self.pirate_handler.dead_pirates:
                    mission.set_amount(mission.amount + 1)

                planet = self.entity_manager.get_component(self.planet_dict[mission.destination], Planet)
                x , y= self.entity_manager.get_component(self.player_id, Position)
                if "moon" in planet.kind:
                    planet = self.entity_manager.get_component(planet.orbits, Planet)

                if mission.amount == mission.max_amount:
                    mission.set_type("complete")
                    for pirate in mission.pirate_ids:
                        self.pirate_handler.unregister_pirate(pirate)
                        self.entity_manager.delete_entity(pirate)
                        mission.pirate_ids.remove(pirate)

                if math.hypot(planet.x - x, planet.y - y) < 800 and mission.active == False:
                    mission.active = True
                    spawn_chunks = find_spawn_chunks_for_planet(self.entity_manager, self.planet_ids, self.planet_dict[planet.name], 30)
                    spawn_planet_siege(self.entity_manager, mission, self.pirate_handler, mission.max_amount - mission.amount, spawn_chunks, planet, self.entity_manager.get_component(planet.orbits, Planet))

                elif math.hypot(planet.x - x, planet.y - y) > 5000:
                    mission.active = True
                    for pirate in mission.pirate_ids:
                        self.pirate_handler.unregister_pirate(pirate)
                        self.entity_manager.delete_entity(pirate)
                        mission.pirate_ids.remove(pirate)

            elif mission.type == "complete":
                if self.camera.selected_planet == None:
                    continue
                    
                if self.camera.selected_planet.name == mission.destination:
                    mission_remove_list.append(mission)
                    bal = self.entity_manager.get_component(self.player_id, Balance)
                    bal.credits += mission.reward

        for mission in mission_remove_list:
            self.hud.log.mission_dict.pop(mission)

        if not self.playing:
            if self.transition_timer != None:
                self.transition_timer -= delta_time

            if self.gameover:
                self.entity_manager.remove_component(self.player_id, pygame.surface.Surface)

            return
        
        elif self.camera.selected_planet != None:
            self.background_system.update(self.camera, delta_time)
            simulated_player = self.simulator.get_simulated_entity(self.player_id)
            self.hud.update(self.entity_manager, self.player_id, self.planet_ids, simulated_player["future_positions"], self.pirate_handler, self.camera, delta_time)
            self.planet_handler.update(self.entity_manager, self.camera, delta_time, True)
            return

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
        ids_list = [self.player_id]
        ids_list.extend(list(self.pirate_handler.pirate_ids))
        self.simulator.simulate(self.entity_manager, ids_list, self.planet_handler.get_planet_imprints(self.entity_manager), 50)

        # Process physics
        self.physics_system.update(self.entity_manager, self.planet_ids, delta_time)

        # Update stars
        self.background_system.update(self.camera, delta_time)

        # Update planets
        self.planet_handler.update(self.entity_manager, self.camera, delta_time)
        self.bullet_system.update(self.entity_manager)
        self.pirate_handler.update(self.entity_manager, self.player_id, self.simulator, delta_time)

        # self.entity_manager.get_component(self.player_id, Position).xy = self.entity_manager.get_component(self.planet_ids[3], Planet).x, self.entity_manager.get_component(self.planet_ids[3], Planet).y
        
        self.timing_system.update(self.entity_manager, delta_time)
        self.health_system.update(self.entity_manager, delta_time)
        self.collision_system.update(self.entity_manager)

        simulated_player = self.simulator.get_simulated_entity(self.player_id)
        self.hud.update(self.entity_manager, self.player_id, self.planet_ids, simulated_player["future_positions"], self.pirate_handler, self.camera, delta_time)
                
    def draw(self, surface: pygame.surface.Surface) -> None:
        self.camera.get_surface().fill((0, 0, 0))
        
        if not self.hud.map.fullscreened or self.hud.map.map_mode == 0: # Render when not fullscreened or when toggled off
            self.background_system.draw(self.camera.get_surface(), self.camera, Images)
            self.planet_handler.draw(self.entity_manager, self.camera, self.camera.get_surface())
            self.animation_system.draw(self.camera.get_surface(), self.entity_manager, self.camera)
            self.camera.draw(self.entity_manager)
            self.bloom_system.draw(self.camera, self.camera.get_surface(), self.entity_manager)
            if self.camera.zoom == 1:
                surface.blit(self.camera.get_surface(), (0, 0))
            else:
                surface.blit(pygame.transform.scale(self.camera.get_surface(), self.camera.screen_size), (0, 0))

            if self.playing:
                for planet_id in self.entity_manager.get_from_components(Planet):
                    planet: Planet = self.entity_manager.get_component(planet_id, Planet)
                    position = self.entity_manager.get_component(self.player_id, Position)

                    if math.hypot(position.x - planet.x, position.y - planet.y) < 350:
                        if self.camera.selected_planet == None:
                            dock_prompt = Images.get_image("dock prompt" + planet.name)

                        else:
                            dock_prompt = Images.get_image("undock prompt")

                        surface.blit(dock_prompt, (1280 / 2- dock_prompt.get_width() / 2, 650))
                        break

        if self.playing:
            self.hud.draw(surface, self.camera)
            return
        
        if not self.gameover:
            surface.fill("#555555", surface.get_rect(), special_flags=BLEND_RGB_MULT)
            image = Images.get_image("pause text")
            prompt_image = Images.get_image("unpause prompt").copy()

        else:
            surface.fill((85, 85, 85, min(self.time_elapsed / self.duration * 255, 255)), surface.get_rect(), special_flags=BLEND_RGBA_MULT)
            image = Images.get_image("gameover text")
            prompt_image = Images.get_image("restart prompt").copy()

            image.set_alpha(self.time_elapsed / self.duration * 255)
            prompt_image.set_alpha(self.time_elapsed / self.duration * 255)

        if self.transition_timer != None:
            if self.transition_timer <= 0:
                self.restart = True
 
            else:
                for i, _ in enumerate(self.prompt_colour):
                    self.prompt_colour[i] = abs(math.sin(math.radians(self.time_elapsed * 800))) * 90
        else:
            for i, _ in enumerate(self.prompt_colour):
                    self.prompt_colour[i] = abs(math.sin(math.radians(self.time_elapsed * 40))) * 60 + 100

        prompt_image.fill(self.prompt_colour, special_flags=BLEND_RGB_SUB)
        surface.blit(image, (surface.get_width() / 2 - image.get_width() / 2, 50))
        pygame.draw.rect(surface, (180, 180, 180), (surface.get_width() / 2 - image.get_width() / 2 - 20, 50 + image.get_height(), image.get_width() + 40, 10))
        surface.blit(prompt_image, (surface.get_width() / 2 - prompt_image.get_width() / 2, 650))

    def stop(self) -> None:
        Sounds.get_sound("bgm").stop()

"""
TODO:
Add recharging / refueling (1)
Add highscore display (1)
Add upgrades / use for money (2)
Link to database (3)
Bug testing (3)
"""
