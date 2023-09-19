import requests
from test_plugin import TestPlugin

class TestFrameworkHealth(TestPlugin):

    def __init__(self, config):
        self.labels = ["TEST-FRAMEWORK-API"]

        if "hostbroker" not in config:
            raise Exception("hostbroker required in config")

        self.host = config["hostbroker"] if config["hostbroker"][-1] != "/" else config["hostbroker"][:-1] 


    def apply(self, options = {}):
        url = self.host + "/health"

        response = requests.get(url)

        return {"success": response.status_code == 200}
