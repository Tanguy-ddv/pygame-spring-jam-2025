# Built-ins
import pygame
import math

# External
import pygame

# Internal
from pygamelib.entities import *
from entities import *

class BulletSystem:
    def update(self, entity_manager: EntityManager):
        entity_ids = entity_manager.get_from_components(Bullet, Timer, Position, Position, CircleCollider, OriginId)

        for entity_id in entity_ids:
            bullet:Bullet = entity_manager.get_component(entity_id, Bullet)
            timer:Timer = entity_manager.get_component(entity_id, Timer)
            position:Position = entity_manager.get_component(entity_id, Position)
            circle_collider:CircleCollider = entity_manager.get_component(entity_id, CircleCollider)
            origin_id:OriginId = entity_manager.get_component(entity_id, OriginId)

            circle_collider.x = position.x + 5 * math.cos(bullet.direction)
            circle_collider.y = position.y - 5 * math.sin(bullet.direction)

            if entity_manager.has_component(entity_id, Collided):
                collided:Collided = entity_manager.get_component(entity_id, Collided)
                for id in collided.other:
                    if id != origin_id.origin_id:
                        if origin_id.origin_id in entity_manager.entity_ids:
                            try:
                                entity_manager.get_component(origin_id.origin_id, OtherIds).remove_other_id(entity_id)
                                entity_manager.delete_entity(entity_id)
                            except:
                                pass # Still found an edge case so just skip it lol?
            
            if timer.time > 1500:
                if origin_id.origin_id in entity_manager.entity_ids:
                    try:
                        entity_manager.delete_entity(entity_id)
                        entity_manager.get_component(origin_id.origin_id, OtherIds).remove_other_id(entity_id)
                    except:
                        pass #ANOTHER EDGE CASE ARE YOU JOKING
