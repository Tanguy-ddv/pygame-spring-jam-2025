import math

class CircleCollider:
    def __init__(self, position: tuple, radius: int, can_collide: bool = True):
        self.x, self.y = position
        self.radius = radius
        self.can_collide = can_collide

    def test_for_collision(self, other_circle: object):
        return math.sqrt((other_circle.x - self.x) ** 2 + (other_circle.y - self.y) ** 2) <= self.radius + other_circle.radius

