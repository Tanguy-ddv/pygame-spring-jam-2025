class Listener:
    def __init__(self, listener_dict: dict):
        self.listener_dict = listener_dict

    def get_subjects(self):
        return self.listener_dict.keys()
    
    def get_observers(self, subject):
        if subject not in self.get_subjects():
            return None
        
        return self.listener_dict[subject]