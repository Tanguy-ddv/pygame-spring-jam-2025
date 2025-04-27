class Fuel:
    def __init__(self, max_fuel: int, fuel:int | float):
        self.max_fuel = max_fuel
        self.fuel = fuel

    def refuel(self, fuel):
        self.fuel = min(self.fuel + fuel, self.max_fuel)
        
    def consume(self, fuel):
        self.fuel = max(self.fuel - fuel, 0)