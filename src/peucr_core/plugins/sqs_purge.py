import boto3
import json
import time

from peucr_core.plugin import TestPlugin

class SqsPurge(TestPlugin):

    def __init__(self, config):
        self.labels = ["SQS-PURGE"]

        self.config = config

        self.client = boto3.client('sqs')


    def apply(self, options = {}):
        if "url" not in options:
            raise Exception("url required in options")

        try:
            self.client.purge_queue(
                    QueueUrl = self.configure(options["url"])
            )

            return {"success": True}

        except Exception as e:
            return {"success": False, "msg": e}
