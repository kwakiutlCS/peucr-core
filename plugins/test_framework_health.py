import requests

class TestFrameworkHealth:

    def __init__(self, config):
        if "hostbroker" not in config:
            raise Exception("hostbroker required in config")

        self.host = config["hostbroker"] if config["hostbroker"][-1] != "/" else config["hostbroker"][:-1] 


    def apply(self, options = {}):
        url = self.host + "/health"

        response = requests.get(url)

        return {"status-code": response.status_code}


    def executes(self, label):
        return label in ["TEST-FRAMEWORK-API", "test-framework-api"]
