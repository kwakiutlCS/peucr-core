import argparse
from test_framework import exec_test_suite, verify_preconditions
from test_compiler import compile_specs, compile_preconditions
import os, json
from plugins import dpp_health, test_framework_health, kafka_consumer_health

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)
    parser.add_argument('--hostdpp', type=str, required=True)
    parser.add_argument('--hostkafka', type=str, required=True)
    parser.add_argument('--hostbroker', type=str, required=True)
    parser.add_argument('--specs', type=str, required=True)

    return parser.parse_args()


def get_configs(args):
    return {k: getattr(args, k) for k in ("username", "password", "hostdpp", "hostkafka", "hostbroker", "specs")}


def load_files(path):
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


if __name__ == "__main__":
    args = parse_args()

    config = get_configs(args)

    config["urlbroker"] = config["hostbroker"]
    config["urldpp"] = config["hostdpp"] + "/dpp/dppsettings/public/v3/blockedusers"
    config["urldpphealth"] = config["hostdpp"] + "/dpp/status/v1/health"
    config["urlkafka"] = config["hostkafka"] + "/health"

    specs = load_files(config["specs"])

    dpp = dpp_health.DppHealth(config)
    testApi = test_framework_health.TestFrameworkHealth(config)
    kafkaConsumer = kafka_consumer_health.KafkaConsumerHealth(config)

    verify_preconditions(compile_preconditions(specs["preconditions"], config), [dpp, testApi, kafkaConsumer])
    exec_test_suite(compile_specs(specs["execution"], config))
