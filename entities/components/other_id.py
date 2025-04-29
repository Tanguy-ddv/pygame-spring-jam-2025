class OtherIds:
    def __init__(self):
        self.other_ids = set()

    def add_other_id(self, other_id:int):
        self.other_ids.add(other_id)

    def remove_other_id(self, other_id:int):
        self.other_ids.add(other_id)

    def check_for_other_id(self, id:int):
        return id in self.other_ids