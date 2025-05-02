# External
import pygame
import math

# Internal
from pygamelib import *
from entities import *

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
