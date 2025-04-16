# Internal
from entities import Entity

class EntityManager:
    def __init__(self):
        self.entities = dict()
        self.components = dict()

        self.next_entity_id = 0

    def create_entity(self) -> Entity:
        entity = Entity(self, self.next_entity_id)

        self.next_entity_id += 1
        self.add_entity(entity)

        return entity 

    def add_entity(self, entity) -> None:
        self.entities[entity.get_id()] = entity

    def register_component(self, entity_id, component_type) -> None:
        entities = self.components.get(component_type, set())
        entities.add(entity_id)

        self.components[component_type] = entities

    def get_entities(self, *component_types) -> set[Entity]:
        entity_ids = list()
        for component_type in component_types:
            entity_ids.append(self.components.get(component_type, set()))

        return [self.get_entity(entity_id) for entity_id in set.intersection(*entity_ids)]
    
    def get_entity(self, entity_id):
        return self.entities[entity_id]