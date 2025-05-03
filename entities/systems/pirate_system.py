# External
import pygame
from pygame.locals import *
import math
import time
import random

# Internal
from pygamelib.entities import *
from entities import *
from assets import *

from ..systems.simulator import SimulationSystem
from ..templates.bullet_template import create_bullet

MAX_RADIANS = math.pi * 2

def get_shortest_distance_in_radians(radians_1:int|float, radians_2:int|float):
    difference = (radians_2 - radians_1) % MAX_RADIANS
    return 2 * difference % MAX_RADIANS - difference

class PirateHandler:
    def __init__(self):
        self.pirate_ids = set()

    def register_pirate(self, id:int):
        self.pirate_ids.add(id)

    def unregister_pirate(self, id:int):
        if id in self.pirate_ids:
            self.pirate_ids.remove(id)

    def update(self, entity_manager: EntityManager, player_id:int, simulator: SimulationSystem):
        player_position:pygame.Vector2 = entity_manager.get_component(player_id, Position)
        player_velocity:pygame.Vector2 = entity_manager.get_component(player_id, Velocity)

        for id in self.pirate_ids.copy():
            position:pygame.Vector2 = entity_manager.get_component(id, Position)
            velocity:pygame.Vector2 = entity_manager.get_component(id, Velocity)
            rotation:Rotation = entity_manager.get_component(id, Rotation)
            force:Force = entity_manager.get_component(id, Force)
            pirate:Pirate = entity_manager.get_component(id, Pirate)
            circle:CircleCollider = entity_manager.get_component(id, CircleCollider)
            other_ids:OtherIds = entity_manager.get_component(id, OtherIds)
            timer:Timer = entity_manager.get_component(id, Timer)
            animator = entity_manager.get_component(id, Animator)
            waypoint:Waypoint = entity_manager.get_component(id, Waypoint)

            simulated_data:dict = simulator.get_simulated_entity(id)

            if not entity_manager.has_component(id, Dying):

                direction = math.radians(rotation.angle)

                direction_to_player = math.atan2((player_position.y - position.y), (player_position.x - position.x))

                if simulated_data["crash"]:
                    pirate.avoid_crash = 20
                if pirate.avoid_crash > 0:
                    pirate.avoid_crash -= 1

                if math.sqrt((position.x - player_position.x) ** 2 + (position.y - player_position.y) ** 2) >= 640:
                    if math.sqrt((velocity.x) ** 2 + (velocity.y) ** 2) >= 350:
                        pirate.slow_down = 10
                if pirate.slow_down > 0:
                    pirate.slow_down -= 1
                
                if pirate.avoid_crash > 0:
                    if len(simulated_data["future_positions"]) > 0:
                        last_position = simulated_data["future_positions"][len(simulated_data["future_positions"]) - 1]
                        direction = math.atan2((last_position[1] - position.y), (last_position[0] - position.x))
                        if id % 2 == 0:
                            direction -= math.radians(90)
                        else:
                            direction += math.radians(90)
                elif pirate.slow_down > 0:
                    direction = math.atan2(velocity.y, velocity.x) + math.radians(180)
                else:
                    direction = math.atan2((player_position.y - position.y), (player_position.x - position.x))

                    if math.degrees(get_shortest_distance_in_radians(math.radians(rotation.angle), -direction)) <= 10:
                        distance = math.sqrt((player_position.x - position.x) ** 2 + (player_position.y - position.y) ** 2)
                        if timer.time % 100 == 0 and distance <= 1280:
                            angle = rotation.angle + random.randint(-4, 4)
                            radians_angle = math.radians(angle)
                            bullet_id = create_bullet(entity_manager, (position.x + 20 * math.cos(radians_angle), position.y - 20 * math.sin(radians_angle)), angle, id)
                            other_ids.add_other_id(bullet_id)
                
                rotation.angle += math.degrees(get_shortest_distance_in_radians(math.radians(rotation.angle), -direction)) / 10
                force.x += 1500 * math.cos(math.radians(rotation.angle))
                force.y -= 1500 * math.sin(math.radians(rotation.angle))

                circle.x, circle.y = position.x, position.y
                waypoint.position.xy = position.xy

                entity_manager.add_component(id, pygame.transform.rotate(Images.get_image("pirate"), rotation.angle - 90))

                if entity_manager.has_component(id, Collided):
                    collided:Collided = entity_manager.get_component(id, Collided)
                    for other_id in collided.other:
                        if not other_id in other_ids.other_ids:
                            animator.animation_stack = {"explosion2": 0}
                            entity_manager.remove_component(id, pygame.Surface)
                            entity_manager.remove_component(id, Simulate)
                            entity_manager.add_component(id, Dying())

            if "explosion2" in animator.animation_stack:
                entity_manager.remove_component(id, pygame.Surface)
                if animator.animation_stack["explosion2"] > 18:
                    entity_manager.delete_entity(id)
                    self.unregister_pirate(id)