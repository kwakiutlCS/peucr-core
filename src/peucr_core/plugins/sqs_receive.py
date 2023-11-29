import boto3
import json
import time

from peucr_core.plugin import TestPlugin

class SqsReceive(TestPlugin):

    def __init__(self, config):
        self.labels = ["SQS-RECEIVE"]

        self.config = config


    def apply(self, options = {}):
        self.client = boto3.client('sqs') if "region" not in options else boto3.client('sqs', region_name=options["region"])
        
        if "sqsReceiveUrl" not in self.config:
            raise Exception("sqsReceiveUrl required in config")

        messageLimit = options["messageLimit"] if options.get("messageLimit") else 10
        duration = options["duration"] if options.get("duration") else 10
        filter = options["filter"] if options.get("filter") else {}

        messages, receipts = self.getMessages(messageLimit, filter, duration)
        self.deleteMessages(receipts)

        success = len(messages) == messageLimit
        msg = None if success else "{:d} messages received, but {:d} were expected".format(len(messages), messageLimit)
        
        return {"success": success, "msg": msg, "json": messages}


    def getMessages(self, limit, filter, duration):
        messages = {}
        start_time = time.time()

        while len(messages) < limit and time.time() < start_time + duration:
            try:
                response = self.client.receive_message(
                        QueueUrl = self.config["sqsReceiveUrl"],
                        MaxNumberOfMessages = limit,
                        WaitTimeSeconds = 2,
                        VisibilityTimeout = 0
                )

                for m in response.get("Messages", []):
                    body = json.loads(m["Body"])

                    if self.isValid(body, filter):
                        messages[m["MessageId"]] = (body, m["ReceiptHandle"])

            except Exception as e:
                pass

        return (list(m[0] for m in messages.values()), list(m[1] for m in messages.values()))


    def isValid(self, message, filter):
        for f in filter.keys():
            if f not in message:
                return False

            if message[f] != filter[f]:
                return False

        return True


    def deleteMessages(self, messages):
        for m in messages:
            self.client.delete_message(
                    QueueUrl = self.config["sqsReceiveUrl"],
                    ReceiptHandle = m
            )
