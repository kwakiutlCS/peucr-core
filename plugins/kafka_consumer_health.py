import requests
from test_plugin import TestPlugin

class KafkaConsumerHealth(TestPlugin):

    def __init__(self, config):
        self.labels = ["DPP-KAFKA-CONSUMER", "KAFKA-CONSUMER"]

        if "hostkafka" not in config:
            raise Exception("hostkafka required in config")

        self.host = config["hostkafka"] if config["hostkafka"][-1] != "/" else config["hostkafka"][:-1] 


    def apply(self, options = {}):
        url = self.host + "/health"

        response = requests.get(url)

        return {"success": response.status_code == 200}
