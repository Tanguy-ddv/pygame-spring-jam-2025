class Health:
    def __init__(self, health:int, invincability:int = 1000):
        self.health = health
        self.invincability_window = invincability
        self.invincability = invincability

    def take_damage(self, damage:int):
        self.health -= damage
        self.invincability = self.invincability_window

    def update_invincability(self, delta_time:float):
        self.invincability -= 1000 * delta_time