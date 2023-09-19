import requests
from requests.auth import HTTPBasicAuth
from test_plugin import TestPlugin

class DppBlockedStatus(TestPlugin):

    def __init__(self, config):
        self.labels = ["DPP-BLOCKED"]

        if "hostdpp" not in config:
            raise Exception("hostdpp required in config")
        if "usernamedpp" not in config:
            raise Exception("usernamedpp required in config")
        if "passworddpp" not in config:
            raise Exception("passworddpp required in config")

        self.host = config["hostdpp"] if config["hostdpp"][-1] != "/" else config["hostdpp"][:-1] 
        self.username = config["usernamedpp"]
        self.password = config["passworddpp"]


    def apply(self, options = {}):
        url = self.host + "/dpp/dppsettings/public/v3/blockedusers"

        if "gcid" not in options:
            raise Exception("gcid required to be passed to options")

        gcid = options["gcid"]
        headers = {"X-rgw-gcid": gcid, "accept": "application/json"}

        auth = HTTPBasicAuth(self.username, self.password)

        response = requests.get(url, auth = auth, headers = headers)

        return {"status-code": response.status_code, "fields": response.json()}
