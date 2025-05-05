class Collided:
    def __init__(self, other_id:input):
        self.other = [other_id]

    def add_other_id(self, other_id:int):
        self.other.append(other_id)

# This represents when a player makes a collision