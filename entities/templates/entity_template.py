import pygame
from entities import *
from pygamelib import *

def create_entity(entity_manager:EntityManager, *args):
    entity_id = entity_manager.create_entity()
    for arg in args:
        entity_manager.add_component(entity_id, arg)
    return entity_id