import boto3
import json
import time

from peucr_core.plugin import TestPlugin

class SqsPurge(TestPlugin):

    def __init__(self, config):
        self.labels = ["SQS-PURGE"]

        self.config = config


    def apply(self, options = {}):
        client = boto3.client('sqs') if "region" not in options else boto3.client('sqs', region_name=options["region"])

        if "url" not in options:
            raise Exception("url required in options")

        try:
            client.purge_queue(
                    QueueUrl = self.configure(options["url"])
            )

            return {"success": True}

        except Exception as e:
            return {"success": False, "msg": e}
