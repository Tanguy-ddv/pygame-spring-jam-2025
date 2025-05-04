import random
import json
import math
from entities import Mission

with open("data/celestial_bodies.json", "r") as file:
    planet_json = json.load(file)
    PLANETS = list(planet_json.keys())
    PLANET_DICT = planet_json
    PLANETS.remove("sun")

with open("data/material_data.json", "r") as file:
    ITEMS = json.load(file)

def new_mission(source):
    mission_type = random.choice(["kill", "deliver"])

    if mission_type == "kill":
        quantity = random.randint(3, 4)
        reward = 0
        destination = random.choice(PLANETS)
        if "moon" not in PLANET_DICT[source]["kind"]:
            destination = random.choice(PLANETS)
            while PLANET_DICT[destination]["orbits"] == source or destination == source:
                destination = random.choice(PLANETS)

        else:
            destination = random.choice(PLANETS)
            while PLANET_DICT[source]["orbits"] == destination or destination == source:
                destination = random.choice(PLANETS)

        for _ in range(quantity):
            reward += random.randint(1737, 3728)

        distance = math.sqrt(abs(PLANET_DICT[source]["dist"] - PLANET_DICT[destination]["dist"]))

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

        if "moon" not in PLANET_DICT[source]["kind"]:
            destination = random.choice(ITEMS[item]["importers"])
            while PLANET_DICT[destination]["orbits"] == source:
                destination = random.choice(ITEMS[item]["importers"])

            distance = abs(PLANET_DICT[source]["dist"] - PLANET_DICT[destination]["dist"])

        else:
            destination = random.choice(ITEMS[item]["importers"])
            while PLANET_DICT[source]["orbits"] == destination:
                destination = random.choice(ITEMS[item]["importers"])

            distance = abs((PLANET_DICT[source]["dist"] + PLANET_DICT[PLANET_DICT[source]["orbits"]]["dist"]) - PLANET_DICT[destination]["dist"])

        distance = math.sqrt(distance)
        quantity = random.randint(ITEMS[item]["lower bound"], ITEMS[item]["upper bound"])
        reward = int(distance * quantity * ITEMS[item]["price"] / 100)
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