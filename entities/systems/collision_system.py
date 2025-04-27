# Built-ins
import math

# External
import pygame

# Internal
from pygamelib.entities import *
from entities import *

from. planet_system import Planet

class CollisionsSystem:
    def update(self, entity_manager: EntityManager, planet_ids: list[int], delta_time: float):
        entity_ids = entity_manager.get_from_components(Position, Health)

        for entity_id in entity_ids:
            # Entity attributes
            position:Position = entity_manager.get_component(entity_id, Position)
            health:Health = entity_manager.get_component(entity_id, Health)

            # Check for planetary collision
            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)

                if max(math.sqrt((planet.x - position.x)** 2 + (planet.y - position.y)**2), 1) < planet.radius:
                    health.take_damage(1000000) #that should be sufficient to kill anything.
                    entity_manager.add_component(entity_id, Collided(planet_id))