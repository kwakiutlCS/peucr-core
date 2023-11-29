import boto3

from peucr_core.plugin import TestPlugin

class SqsSend(TestPlugin):

    def __init__(self, config):
        self.labels = ["SQS-SEND"]

        self.config = config


    def apply(self, options = {}):
        client = boto3.client('sqs') if "region" not in options else boto3.client('sqs', region_name=options["region"])

        if "sqsSendUrl" not in self.config:
            raise Exception("sqsSendUrl required in config")

        if options.get("body"):
            message = options["body"]
        else:
            raise Exception("SQS-SEND requires body in options.")

        msg = None 
        success = False

        try:
            response = client.send_message(
                QueueUrl=self.config["sqsSendUrl"],
                MessageBody=message
            )
            success = True

        except Exception as e:
            msg = e

        return {"success": success, "msg": msg}
