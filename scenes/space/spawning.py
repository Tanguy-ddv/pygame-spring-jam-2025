# External
import pygame
import math
import random

# Internal
from pygamelib import *
from entities import *
from assets import *

def find_spawn_chunks_for_planet(entity_manager: EntityManager, planet_ids: list[int], target_planet_id:int, chunk_size:int):
    planet_moons = []
    for planet_id in planet_ids:
        planet:Planet = entity_manager.get_component(planet_id, Planet)
        if planet.orbits == target_planet_id:
            planet_moons.append(planet_id)

    half_chunk_size = (chunk_size / 2)
    
    planet_chunks = {}
    for chunk in range(math.floor(360 / chunk_size)):
        planet_chunks[chunk * chunk_size + half_chunk_size] = False
    
    planet:Planet = entity_manager.get_component(target_planet_id, Planet)
    for planet_id in planet_moons:
        moon:Planet = entity_manager.get_component(planet_id, Planet)
        chunk = math.floor(moon.theta / chunk_size) * chunk_size + half_chunk_size
        planet_chunks[chunk] = True

    return planet_chunks

def spawn_planet_siege(entity_manager: EntityManager, pirate_handler: PirateHandler, pirates: int, spawn_chunks: dict, planet: Planet, planet_orbits: Planet):
    for i in range(pirates):
        spawn_chunk = 15
        while spawn_chunks[spawn_chunk] != False:
            spawn_chunk = random.randint(0, 11) * 30 + 15
        spawn_chunks[spawn_chunk] = True
        dist = (planet.dist + planet.radius + planet_orbits.radius)
        spawn_position = (planet_orbits.x + dist * math.cos(math.radians(planet.theta))), planet_orbits.y + dist * math.sin(math.radians(planet.theta))
        spawn_position = (spawn_position[0] + math.cos(math.radians(spawn_chunk)) * planet.diameter * 5, spawn_position[1] + math.sin(math.radians(spawn_chunk)) * planet.diameter * 5)
        pirate_id = create_pirate(entity_manager,
                                  spawn_position,
                                  Images.get_image("pirate"))
            
        pirate_handler.register_pirate(pirate_id)
