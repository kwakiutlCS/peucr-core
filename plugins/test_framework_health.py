import requests

class TestFrameworkHealth:

    def __init__(self, config):
        if "hostbroker" not in config:
            raise Exception("hostbroker required in config")

        self.host = config["hostbroker"] if config["hostbroker"][-1] != "/" else config["hostbroker"][:-1] 


    def apply(self):
        url = self.host + "/health"

        return requests.get(url)


    def executes(self, label):
        return label in ["TEST-FRAMEWORK-API", "test-framework-api"]

