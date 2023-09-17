import argparse
from test_framework import TestFramework
from test_compiler import compile_specs, compile_preconditions
import os, json
from plugins import dpp_health, test_framework_health, kafka_consumer_health, dpp_blocked_status, kafka_block_user, kafka_unblock_user

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


def load_specs(path):
    specs = {}
    if "_spec.json" in path:
        directory = "/".join(path.split("/")[:-1])
        files = os.listdir(directory)
        spec_files = [path.split("/")[-1]]
    else:
        directory = path
        files = os.listdir(directory)
        spec_files = [file for file in files if "_spec.json" in file]
        spec_files.sort()
    
    preconditions = directory+"/preconditions.json" if "preconditions.json" in files else None

    if preconditions:
        with open(preconditions, "r") as p:
            specs["preconditions"] = json.loads(p.read())

    execution = []
    for file in spec_files:
        with open(directory+"/"+file, "r") as f:
            execution.append(json.loads(f.read()))

    specs["execution"] = execution

    return specs


def load_plugins(config):
    return [
        dpp_health.DppHealth(config),
        test_framework_health.TestFrameworkHealth(config),
        kafka_consumer_health.KafkaConsumerHealth(config),
        dpp_blocked_status.DppBlockedStatus(config),
        kafka_block_user.BlockUser(config),
        kafka_unblock_user.UnblockUser(config)
    ]


if __name__ == "__main__":
    args = parse_args()

    config = get_configs(args)

    config["urlbroker"] = config["hostbroker"]

    specs = load_specs(config["specs"])
    plugins = load_plugins(config)

    framework = TestFramework(plugins, config)

    if "preconditions" in specs:
        framework.verify_preconditions(compile_preconditions(specs["preconditions"], config))

    framework.exec_test_suite(compile_specs(specs["execution"], config))
