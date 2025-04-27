# Built-ins
import math

# External
import pygame

# Internal
from pygamelib.entities import *
from entities import *

from. planet_system import Planet

class PhysicsSystem:
    def update(self, entity_manager: EntityManager, planet_ids: list[int], delta_time: float):
        entity_ids = entity_manager.get_from_components(Position, Velocity, Force, Mass)

        for entity_id in entity_ids:
            # Entity attributes
            position:Position = entity_manager.get_component(entity_id, Position)
            velocity = entity_manager.get_component(entity_id, Velocity)
            force:Force = entity_manager.get_component(entity_id, Force)
            mass = entity_manager.get_component(entity_id, Mass)

            for planet_id in planet_ids:
                planet:Planet = entity_manager.get_component(planet_id, Planet)
                if planet.kind != "moon":
                    multiplier = 1
                    if planet.kind == "sun":
                        multiplier = 5

                    direction = math.atan2((planet.y - position.y), (planet.x - position.x))
                    distance = max(math.sqrt((planet.x - position.x)** 2 + (planet.y - position.y)**2), 1)
                    force.x += (9.81 * math.cos(direction) * (mass.magnitude * planet.mass) / distance) * multiplier
                    force.y += (9.81 * math.sin(direction) * (mass.magnitude * planet.mass) / distance) * multiplier
            
            # Update motion
            velocity += force / mass.get_mass() * delta_time
            position += velocity * delta_time

            # Reset force each frame
            entity_manager.add_component(entity_id, Force(0, 0))
    