class Listener:
    def __init__(self, observer: object, subject: int):
        self.observer = observer
        self.subject = subject

    def get_observer(self):
        return self.observer

    def get_subject(self):
        return self.subject