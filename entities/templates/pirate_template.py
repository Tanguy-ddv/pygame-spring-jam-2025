import pygame
from entities import *
from pygamelib import *
from .entity_template import create_entity

def create_pirate(entity_manager: EntityManager, position:tuple, surface: pygame.Surface):
    pirate = create_entity(entity_manager,
                         Position(position),
                         Velocity(0, 0),
                         Force(0, 0),
                         Mass(20),
                         CircleCollider((0, 0), 9),
                         OtherIds(),
                         Simulate(),
                         Rotation(0),
                         Pirate(),
                         Health(1),
                         Timer(),
                         surface,
                         Animator()
                         )
    
    entity_manager.get_component(pirate, Animator).animation_stack["pirate main drive hold"] = 0
    return pirate