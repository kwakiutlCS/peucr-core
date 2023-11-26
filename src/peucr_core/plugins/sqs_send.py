import boto3

from peucr_core.plugin import TestPlugin

class SqsSend(TestPlugin):

    def __init__(self, config):
        self.labels = ["SQS-SEND"]

        self.config = config

        self.client = boto3.client('sqs')


    def apply(self, options = {}):
        if "sqsSendUrl" not in self.config:
            raise Exception("sqsSendUrl required in config")

        if options.get("body"):
            message = options["body"]
        else:
            raise Exception("SQS-SEND requires body in options.")

        msg = None 
        success = False

        try:
            response = self.client.send_message(
                QueueUrl=self.config["sqsSendUrl"],
                MessageBody=message
            )
            success = True

        except Exception as e:
            msg = e

        return {"success": success, "msg": msg}
