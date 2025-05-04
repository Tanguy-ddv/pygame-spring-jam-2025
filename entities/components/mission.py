class Mission:
    def __init__(self, mission_type, max_amount, item, destination, source, reward, unit):
        self.source = source
        self.destination = destination
        self.max_amount = max_amount
        self.item = item

        self.last_type = mission_type
        self.type = mission_type
        self.reward = reward
        self.unit = unit

        self.active = False
        self.last_amount = 0
        self.amount = 0

    def set_amount(self, new_amount):
        self.last_amount = self.amount
        self.amount = new_amount

    def set_type(self, new_type):
        self.last_type = self.type
        self.type = new_type