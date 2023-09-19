import requests
from test_plugin import TestPlugin

class UnblockUser(TestPlugin):

    def __init__(self, config):
        self.labels = ["UNBLOCK"]
        
        if "hostbroker" not in config:
            raise Exception("hostbroker required in config")

        self.host = config["hostbroker"] if config["hostbroker"][-1] != "/" else config["hostbroker"][:-1] 


    def apply(self, options = {}):
        url = self.host + "/unblockUser"

        if options.get("body"):
            body = { "content": options["body"] }
        elif options.get("gcid"):
            body = {
                "content":"{\"AccountActivation\":{\"gcid\":\"" + options["gcid"] + "\"}}"        
            }
        else:
            raise Exception("Unblock user requires options with json body or gcid")

        response = requests.post(url, json=body)

        return {"success": response.status_code == 200}
