import random
import json
from entities import Mission

with open("data/celestial_bodies.json", "r") as file:
    planet_json = json.load(file)
    PLANETS = list(planet_json.keys())
    PLANETS.remove("sun")

with open("data/material_data.json", "r") as file:
    ITEMS = json.load(file)

def new_mission(source):
    mission_type = random.choice(["kill", "deliver"])

    if mission_type == "kill":
        quantity = random.randint(3, 8)
        reward = 0
        destination = random.choice(PLANETS)
        while destination == source:
            destination = random.choice(PLANETS)

        for _ in range(quantity):
            reward += random.randint(7432, 9042)

        return Mission(
            mission_type,
            quantity,
            "pirates",
            destination,
            source,
            reward,
            None
        )
    
    elif mission_type == "deliver":
        item = random.choice(list(ITEMS.keys()))
        while source not in ITEMS[item]["exporters"]:
            item = random.choice(list(ITEMS.keys()))

        destination = random.choice(ITEMS[item]["importers"])
        quantity = random.randint(ITEMS[item]["lower bound"], ITEMS[item]["upper bound"])
        reward = int(quantity * ITEMS[item]["price"])
        unit = ITEMS[item]["unit"]

        return Mission(
            mission_type,
            quantity,
            item,
            destination,
            source,
            reward,
            unit
        )