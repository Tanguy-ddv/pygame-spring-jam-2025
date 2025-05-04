import pygame
import math
from entities import *
from pygamelib import *
from .entity_template import create_entity
from assets import *

def create_bullet(entity_manager: EntityManager, position:tuple, direction:int, origin_id:int):
    return create_entity(entity_manager, 
                         Position(position),
                         Velocity(0, 0),
                         Mass(0.00001),
                         Force(1 * math.cos(math.radians(direction)), -1 * math.sin(math.radians(direction))),
                         pygame.transform.rotate(Images.get_image("laser"), direction),
                         Timer(),
                         Bullet(direction),
                         CircleCollider(position, 4),
                         OriginId(origin_id),
                         Simulate() # This is needed for all entities using the physics system
                         )
            