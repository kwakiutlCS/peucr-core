import requests

class KafkaConsumerHealth:

    def __init__(self, config):
        if "hostkafka" not in config:
            raise Exception("hostkafka required in config")

        self.host = config["hostkafka"] if config["hostkafka"][-1] != "/" else config["hostkafka"][:-1] 


    def apply(self, options = {}):
        url = self.host + "/health"

        response = requests.get(url)

        return {"status-code": response.status_code}


    def executes(self, label):
        return label in ["DPP-KAFKA-CONSUMER", "dpp-kafka-consumer",  "KAFKA-CONSUMER", "kafka-consumer"]
