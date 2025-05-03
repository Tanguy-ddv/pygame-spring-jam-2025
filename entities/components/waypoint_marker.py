import pygame

class Waypoint:
    def __init__(self, position:pygame.Vector2, max_viewable_distance:int, color:int):
        self.position = position
        self.max_viewable_distance = max_viewable_distance
        self.color = color
