import requests
from test_plugin import TestPlugin

class DppHealth(TestPlugin):

    def __init__(self, config):
        self.labels = ["DPP", "DPP-HEALTH"]

        if "hostdpp" not in config:
            raise Exception("hostdpp required in config")

        self.host = config["hostdpp"] if config["hostdpp"][-1] != "/" else config["hostdpp"][:-1] 


    def apply(self, options = {}):
        url = self.host + "/dpp/status/v1/health"

        response = requests.get(url)

        return {"success": response.status_code == 200}
