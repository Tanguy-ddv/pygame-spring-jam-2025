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

    def update(self, entity_manager: EntityManager, player_id:int):
        player_position:pygame.Vector2 = entity_manager.get_component(player_id, Position)

        for id in self.pirate_ids:
            position:pygame.Vector2 = entity_manager.get_component(id, Position)
            rotation:Rotation = entity_manager.get_component(id, Rotation)
            force:Force = entity_manager.get_component(id, Force)
            surface:pygame.Surface = entity_manager.get_component(id, pygame.Surface)

            direction_to_player = math.atan2((player_position.y - position.y), (player_position.x - position.x))
            rotation.angle += math.degrees(get_shortest_distance_in_radians(math.radians(rotation.angle), direction_to_player)) / 10
            force.x += 2000 * math.cos(math.radians(rotation.angle))
            force.y += 2000 * math.sin(math.radians(rotation.angle))

            entity_manager.add_component(id, pygame.transform.rotate(Images.get_image("pirate"), -rotation.angle))
