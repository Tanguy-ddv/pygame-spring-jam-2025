# Built-ins
from __future__ import annotations

class Entity:
    def __init__(self, entity_manager: EntityManager, entity_id: int):
        self.entity_manager: EntityManager = entity_manager
        self.entity_id: int = entity_id
        self.component_dict: dict[type, object] = {}

        self.entity_manager.register_entity(self.entity_id, self)

    def __del__(self) -> None:
        self.kill()

    def get_id(self) -> int:
        return self.entity_id
    
    def add_component(self, component: object) -> None:
        component_type = type(component)

        self.component_dict[component_type] = component
        self.entity_manager.register_component(self.entity_id, component_type)

    def remove_component(self, component_type: type) -> None:
        self.component_dict.pop(component_type)
        self.entity_manager.unregister_component(self.entity_id, component_type)
    
    def get_component(self, component_type: type) -> object:
        return self.component_dict[component_type]
    
    def kill(self) -> None:
        for component_type in self.component_dict.keys():
            self.remove_component(component_type)

        self.entity_manager.unregister_entity(self.entity_id)

class EntityManager:
    def __init__(self):
        self.entity_dict: dict[int, object] = {}
        self.component_dict: dict[type, set] = {}

        self.next_entity_id = 0

    def create_entity(self) -> Entity:
        entity = Entity(self, self.next_entity_id)
        self.next_entity_id += 1

        return entity
    
    def register_entity(self, entity_id: int, entity: Entity) -> None:
        self.entity_dict[entity_id] = entity

    def register_component(self, entity_id: int, component_type: type) -> None:
        entities = self.component_dict.get(component_type, set())
        entities.add(entity_id)

        self.component_dict[component_type] = entities

    def unregister_entity(self, entity_id: int) -> None:
        if entity_id not in self.entity_dict.keys():
            return

        self.entity_dict.pop(entity_id)

    def unregister_component(self, entity_id: int, component_type: type) -> None:
        entities = self.component_dict.get(component_type, set())
        entities.remove(entity_id)

        self.component_dict[component_type] = entities

    def get_from_components(self, *component_types: type) -> set[Entity]:
        entity_ids = []
        for component_type in component_types:
            entity_ids.append(self.component_dict.get(component_type, set()))

        return [self.get_from_id(entity_id) for entity_id in set.intersection(*entity_ids)]
    
    def get_from_id(self, entity_id: int) -> Entity:
        return self.entity_dict[entity_id]