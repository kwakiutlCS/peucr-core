import requests

class DppHealth:

    def __init__(self, config):
        if "hostdpp" not in config:
            raise Exception("hostdpp required in config")

        self.host = config["hostdpp"] if config["hostdpp"][-1] != "/" else config["hostdpp"][:-1] 


    def apply(self):
        url = self.host + "/dpp/status/v1/health"

        return requests.get(url)


    def executes(self, label):
        return label in ["DPP", "dpp", "Dpp", "DPP_HEALTH", "dpp_health", "DPP-HEALTH", "dpp-health"]
