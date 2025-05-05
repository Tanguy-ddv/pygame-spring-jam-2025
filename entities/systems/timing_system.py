# Internal
from pygamelib.entities import *
from entities import *
from ..components import Timer

class TimingSystem:
    def update(self, entity_manager: EntityManager, delta_time: float):
        entity_ids = entity_manager.get_from_components(Timer)

        for entity_id in entity_ids:
            # Entity attributes
            time:Timer = entity_manager.get_component(entity_id, Timer)
            time.time += 1000 * delta_time