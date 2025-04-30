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
        self.pirate_ids.remove(id)

    def update(self, entity_manager: EntityManager, player_id:int, simulator: SimulationSystem):
        player_position:pygame.Vector2 = entity_manager.get_component(player_id, Position)

        for id in self.pirate_ids:
            position:pygame.Vector2 = entity_manager.get_component(id, Position)
            rotation:Rotation = entity_manager.get_component(id, Rotation)
            force:Force = entity_manager.get_component(id, Force)
            surface:pygame.Surface = entity_manager.get_component(id, pygame.Surface)
            pirate:Pirate = entity_manager.get_component(id, Pirate)

            simulated_data:dict = simulator.get_simulated_entity(id)

            direction = math.radians(rotation.angle)

            if simulated_data["crash"]:
                pirate.avoid_crash = 15
            else:
                if pirate.avoid_crash > 0:
                    pirate.avoid_crash -= 1
            if pirate.avoid_crash > 0:
                if len(simulated_data["future_positions"]) > 0:
                    last_position = simulated_data["future_positions"][len(simulated_data["future_positions"]) - 1]
                    direction = math.atan2((last_position[1] - position.y), (last_position[0] - position.x))
                    if id % 2 == 0:
                        direction -= math.radians(90)
                    else:
                        direction += math.radians(90)
            else:
                direction = math.atan2((player_position.y - position.y), (player_position.x - position.x))
            rotation.angle += math.degrees(get_shortest_distance_in_radians(math.radians(rotation.angle), direction)) / 10
            force.x += 1500 * math.cos(math.radians(rotation.angle))
            force.y += 1500 * math.sin(math.radians(rotation.angle))

            entity_manager.add_component(id, pygame.transform.rotate(Images.get_image("pirate"), -rotation.angle))