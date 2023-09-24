import re

class TestPlugin:

    def __init__(self):
        self.labels = []

    def executes(self, name):
        return name.upper() in [l.upper() for l in self.labels]

    def configure(self, value, config):
        pattern = r"\$\{([^}]+)\}"

        m = re.search(pattern, value)

        if m is None:
            return value

        for key in m.groups():
            if config.get(key):
                value = value.replace("${" + key + "}", config[key])
        
        return value
