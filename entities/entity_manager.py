# Built-ins
from __future__ import annotations
from typing import Type

class Entity:
    def __init__(self, entity_manager: EntityManager, entity_id: int):
        self.entity_manager = entity_manager
        self.entity_id = entity_id

        self.components = {}

    def add_component(self, component: object) -> None:
        component_type = type(component)

        self.components[component_type] = component
        self.entity_manager.register_component(self.entity_id, component_type)

    def get_id(self) -> int:
        return self.entity_id
    
    def get_component(self, component_type: Type) -> object:
        return self.components[component_type]    

class EntityManager:
    def __init__(self):
        self.entities = {}
        self.components = {}

        self.next_entity_id = 0

    def create_entity(self) -> Entity:
        entity = Entity(self, self.next_entity_id)

        self.next_entity_id += 1
        self.register_entity(entity)

        return entity
    
    def register_entity(self, entity: Entity) -> None:
        self.entities[entity.get_id()] = entity

    def register_component(self, entity_id: int, component_type: Type) -> None:
        entities = self.components.get(component_type, set())
        entities.add(entity_id)

        self.components[component_type] = entities

    def get_entities(self, *component_types: Type) -> set[Entity]:
        entity_ids = []
        for component_type in component_types:
            entity_ids.append(self.components.get(component_type, set()))

        return [self.get_entity(entity_id) for entity_id in set.intersection(*entity_ids)]
    
    def get_entity(self, entity_id: int) -> Entity:
        return self.entities[entity_id]