import requests
from peucr_core_ricardo_rodrigues.plugin import TestPlugin

class HttpPlugin(TestPlugin):

    def __init__(self, config):
        self.labels = ["HTTP"]
        self.config = config


    def apply(self, options = {}):
        url = self.configure(options.get("url"), self.config)

        response = requests.get(url)

        return {"success": response.status_code >= 200 and response.status_code < 300}
