class Shield:
    def __init__(self):
        self.activated = False

    def down(self):
        self.activated = False
    
    def up(self):
        self.activated = True