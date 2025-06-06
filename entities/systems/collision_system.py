# Built-ins
import math

# External
import pygame

# Internal
from pygamelib.entities import *
from entities import *

from. planet_system import Planet

class CollisionsSystem:
    def update(self, entity_manager: EntityManager):
        entity_ids = entity_manager.get_from_components(Collided)
        for entity_id in entity_ids:
            entity_manager.remove_component(entity_id, Collided)
        
        entity_ids_a = entity_manager.get_from_components(CircleCollider)
        entity_ids_b = entity_manager.get_from_components(CircleCollider)

        for entity_id_a in entity_ids_a:
            entity_a_circle:CircleCollider = entity_manager.get_component(entity_id_a, CircleCollider)
            if entity_a_circle.can_collide:
                for entity_id_b in entity_ids_b:
                    entity_b_circle:CircleCollider = entity_manager.get_component(entity_id_b, CircleCollider)
                    collision_check = True
                    if entity_id_a == entity_id_b:
                        collision_check = False
                    if collision_check:
                        if entity_a_circle.test_for_collision(entity_b_circle):
                            if entity_manager.has_component(entity_id_a, Collided):
                                entity_manager.get_component(entity_id_a, Collided).add_other_id(entity_id_b)
                            else:
                                entity_manager.add_component(entity_id_a, Collided(entity_id_b))
                            if entity_manager.has_component(entity_id_b, Collided):
                                entity_manager.get_component(entity_id_b, Collided).add_other_id(entity_id_a)
                            else:
                                entity_manager.add_component(entity_id_b, Collided(entity_id_a))