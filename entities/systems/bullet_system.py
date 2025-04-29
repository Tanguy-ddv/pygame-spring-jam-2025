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
        entity_ids = entity_manager.get_from_components(Bullet, Timer, Position, CircleCollider)

        for entity_id in entity_ids:
            bullet:Bullet = entity_manager.get_component(entity_id, Bullet)
            timer:Timer = entity_manager.get_component(entity_id, Timer)
            position:Position = entity_manager.get_component(entity_id, Position)
            circle_collider:CircleCollider = entity_manager.get_component(entity_id, CircleCollider)

            if timer.time > 5000:
                entity_manager.delete_entity(entity_id)

            circle_collider.x = position.x + 5 * math.cos(bullet.direction)
            circle_collider.y = position.y - 5 * math.sin(bullet.direction)

            if entity_manager.has_component(entity_id, Collided):
                entity_manager.delete_entity(entity_id)
