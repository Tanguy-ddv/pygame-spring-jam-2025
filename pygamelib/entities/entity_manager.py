# Internal
from utils import Singleton

# Entity Manager class
class EntityManager(Singleton):
    def __init__(self):
        self.entity_ids: set[int] = set()
        self.free_ids: set[int] = set()
        self.next_id: int = 0

        self.component_dict: dict[type, dict[int, object]] = {}

    def create_entity(self) -> int:
        if self.free_ids:
            entity_id = self.free_ids.pop()

        else:
            entity_id = self.next_id
            self.next_id += 1

        self.entity_ids.add(entity_id)
        return entity_id
    
    def add_component(self, entity_id: int, component: object) -> None:
        if entity_id not in self.entity_ids:
            return
        
        component_type = type(component)
        self.component_dict.setdefault(component_type, {})[entity_id] = component

    def has_component(self, entity_id: int, component_type: type) -> bool:
        if entity_id not in self.entity_ids:
            return False
        
        return entity_id in self.component_dict.get(component_type, {})
    
    def get_component(self, entity_id: int, component_type: type) -> object:
        if not self.has_component(entity_id, component_type):
            return
        
        return self.component_dict[component_type][entity_id]

    def remove_component(self, entity_id: int, component_type: type) -> None:
        components = self.component_dict.get(component_type)
        if entity_id not in self.entity_ids or components is None:
            return

        components.pop(entity_id, None)
        if not components:
            self.component_dict.pop(component_type)

    def delete_entity(self, entity_id: int) -> None:
        if entity_id not in self.entity_ids:
            return
        
        self.entity_ids.remove(entity_id)
        self.free_ids.add(entity_id)

        for component_type in list(self.component_dict.keys()):
            self.remove_component(entity_id, component_type)