import argparse
from test_framework import TestFramework
import os, json
from plugins import dpp_health, test_framework_health, kafka_consumer_health, dpp_blocked_status, kafka_block_user, kafka_unblock_user
from test_spec_loader import SpecLoader

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--usernamedpp', type=str, required=True)
    parser.add_argument('--passworddpp', type=str, required=True)
    parser.add_argument('--hostdpp', type=str, required=True)
    parser.add_argument('--hostkafka', type=str, required=True)
    parser.add_argument('--hostbroker', type=str, required=True)
    parser.add_argument('--specs', type=str, required=True)

    return parser.parse_args()


def get_configs(args):
    return {k: getattr(args, k) for k in ("usernamedpp", "passworddpp", "hostdpp", "hostkafka", "hostbroker", "specs")}


if __name__ == "__main__":
    args = parse_args()
    config = get_configs(args)

    specs = SpecLoader().apply(config["specs"])
    plugins = [
        dpp_health.DppHealth(config),
        test_framework_health.TestFrameworkHealth(config),
        kafka_consumer_health.KafkaConsumerHealth(config),
        dpp_blocked_status.DppBlockedStatus(config),
        kafka_block_user.BlockUser(config),
        kafka_unblock_user.UnblockUser(config)
    ]

    framework = TestFramework(plugins)

    framework.verify_preconditions(specs.get("preconditions"))

    framework.exec_test_suite(specs.get("execution"))
