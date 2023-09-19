class TestPlugin:

    def __init__(self):
        self.labels = []

    def executes(self, name):
        return name.upper() in [l.upper() for l in self.labels]
