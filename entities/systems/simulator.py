# External
import pygame
import math

# Internal
from pygamelib import *
from entities import *
from utils.constants import GAMEH_PER_REALSEC

from .planet_system import PlanetImprint

class SimulationSystem:
    def __init__(self):
        self.simulated_entities = {}
    
    def simulate(self, entity_manager:EntityManager, entity_ids:list[int], planet_imprints:dict[int:PlanetImprint], i:int):
        self.simulated_entities.clear()
        
        for entity_id in entity_ids:
            self.simulated_entities[entity_id] = {"position":Position(entity_manager.get_component(entity_id, Position).xy),
                                                "velocity":Velocity(entity_manager.get_component(entity_id, Velocity).xy),
                                                "force":Force(entity_manager.get_component(entity_id, Force).xy),
                                                "mass":Mass((entity_manager.get_component(entity_id, Mass).get_mass())),
                                                "future_positions":[],
                                                "crash":False,
                                                "crash_reason":None,
                                                }
            if entity_manager.has_component(entity_id, CircleCollider):
                circle_collider:CircleCollider = entity_manager.get_component(entity_id, CircleCollider)
                self.simulated_entities[entity_id]["circle_collider"] = CircleCollider((circle_collider.x, circle_collider.y), circle_collider.radius, circle_collider.can_collide)
            else:
                self.simulated_entities[entity_id]["circle_collider"] = None
            
            dt = 0.05

            j = 0

        while j < i:
            #updating planet orbits
            for planet_id, planet_imprint in planet_imprints.items():
                planet_imprint:PlanetImprint
                if planet_imprint.orbits is not None:
                    planet_imprint.theta = (dt/planet_imprint.year*24*GAMEH_PER_REALSEC + planet_imprint.theta)%360

                    orbit:PlanetImprint = planet_imprints[planet_imprint.orbits]

                    planet_imprint.x, planet_imprint.y = orbit.x + (planet_imprint.dist + orbit.radius + planet_imprint.radius)*math.cos(planet_imprint.theta*math.pi/180), orbit.y + (planet_imprint.dist + orbit.radius + planet_imprint.radius)*math.sin(planet_imprint.theta*math.pi/180)
            
            # updating circle_colliders:
            for entity_id in self.simulated_entities:
                if self.simulated_entities[entity_id]["crash"] == False:
                    entity_circle_collider:CircleCollider = self.simulated_entities[entity_id]["circle_collider"]
                    if entity_circle_collider != None:
                        entity_circle_collider.x, entity_circle_collider.y = self.simulated_entities[entity_id]["position"].xy

            # testing for planet collisions
            for entity_id in self.simulated_entities:
                if self.simulated_entities[entity_id]["crash"] == False:
                    entity_circle_collider:CircleCollider = self.simulated_entities[entity_id]["circle_collider"]
                    if entity_circle_collider != None:
                        for planet in planet_imprints.values():
                            if math.sqrt((planet.x - entity_circle_collider.x) ** 2 + (planet.y - entity_circle_collider.y) ** 2) <= planet.radius + entity_circle_collider.radius:
                                self.simulated_entities[entity_id]["crash"] = True
                                self.simulated_entities[entity_id]["crash_reason"] = "planet"

            # testing for other object collisions
            for entity_id_a in self.simulated_entities:
                entity_a_circle_collider:CircleCollider = self.simulated_entities[entity_id_a]["circle_collider"]
                if entity_a_circle_collider != None:
                    if entity_a_circle_collider.can_collide:
                        for entity_id_b in self.simulated_entities:
                            entity_b_circle_collider:CircleCollider = self.simulated_entities[entity_id_b]["circle_collider"]
                            if entity_id_b != entity_id_a and entity_b_circle_collider != None:
                                if math.sqrt((entity_a_circle_collider.x - entity_b_circle_collider.x) ** 2 + (entity_a_circle_collider.y - entity_b_circle_collider.y) ** 2) <= entity_a_circle_collider.radius + entity_b_circle_collider.radius:
                                    self.simulated_entities[entity_id]["crash"] = True
                                    self.simulated_entities[entity_id]["crash_reason"] = "object"

            for entity_id in self.simulated_entities:
                if self.simulated_entities[entity_id]["crash"] == False:
                    for planet_id in planet_imprints:
                        planet = planet_imprints[planet_id]
                        distance = max(math.sqrt((planet.x - self.simulated_entities[entity_id]["position"].x)** 2 + (planet.y - self.simulated_entities[entity_id]["position"].y)**2), 1)
                        if planet.kind == "moon":
                            continue # skip moons due to difficulty orbiting planets (n-body problem)

                        direction = math.atan2((planet.y - self.simulated_entities[entity_id]["position"].y), (planet.x - self.simulated_entities[entity_id]["position"].x))
                        self.simulated_entities[entity_id]["force"].x += 9.81 * math.cos(direction) * (self.simulated_entities[entity_id]["mass"].magnitude * planet.mass) / distance
                        self.simulated_entities[entity_id]["force"].y += 9.81 * math.sin(direction) * (self.simulated_entities[entity_id]["mass"].magnitude * planet.mass) / distance
                        
                    # Update motion
                    self.simulated_entities[entity_id]["velocity"] += self.simulated_entities[entity_id]["force"] / self.simulated_entities[entity_id]["mass"].get_mass() * dt
                    self.simulated_entities[entity_id]["position"] += self.simulated_entities[entity_id]["velocity"] * dt

                    # Reset force each frame
                    self.simulated_entities[entity_id]["force"].xy = 0, 0

                    self.simulated_entities[entity_id]["future_positions"].append(self.simulated_entities[entity_id]["position"].xy)
            j += 1

    def get_simulated_entity(self, entity_id:int):
        return self.simulated_entities[entity_id]