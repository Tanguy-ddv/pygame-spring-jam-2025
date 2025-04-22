# Internal
from pygamelib.entities import *
from entities import *

class PhysicsSystem:
    def update(self, entity_manager: EntityManager, delta_time: float):
        entity_ids = entity_manager.get_from_components(Position, Velocity, Force, Mass)

        for entity_id in entity_ids:
            # Entity attributes
            position = entity_manager.get_component(entity_id, Position)
            velocity = entity_manager.get_component(entity_id, Velocity)
            force = entity_manager.get_component(entity_id, Force)
            mass = entity_manager.get_component(entity_id, Mass)

            # Update motion
            velocity += force / mass.get_mass() * delta_time
            position += velocity * delta_time

            # Reset force each frame
            entity_manager.add_component(entity_id, Force(0, 0))