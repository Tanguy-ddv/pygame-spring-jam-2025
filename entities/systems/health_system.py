# External
import pygame

# Internal
from pygamelib import *
from entities import *

class HealthSystem:
    def update(self, entity_manager: EntityManager, delta_time: float):
        entity_ids = entity_manager.get_from_components(Health)

        for entity_id in entity_ids:
            health:Health = entity_manager.get_component(entity_id, Health)
            health.update_invincability(delta_time)