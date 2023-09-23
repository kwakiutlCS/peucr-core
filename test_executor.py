import argparse
from test_framework import TestFramework
from test_spec_loader import SpecLoader
from test_plugin_loader import PluginLoader

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--usernamedpp', type=str, required=True)
    parser.add_argument('--passworddpp', type=str, required=True)
    parser.add_argument('--hostdpp', type=str, required=True)
    parser.add_argument('--hostkafka', type=str, required=True)
    parser.add_argument('--hostbroker', type=str, required=True)
    parser.add_argument('--specs', type=str, required=True)
    parser.add_argument('--plugins', type=str, required=True)

    return parser.parse_args()


def get_configs(args):
    return {k: getattr(args, k) for k in ("usernamedpp", "passworddpp", "hostdpp", "hostkafka", "hostbroker", "specs", "plugins")}


if __name__ == "__main__":
    args = parse_args()
    config = get_configs(args)

    specs = SpecLoader().apply(config["specs"])
    plugins = PluginLoader().apply(config["plugins"])
    plugins = [plugin(config) for plugin in plugins]

    framework = TestFramework(plugins)

    framework.exec_preconditions(specs.get("preconditions"))

    framework.exec_test_suite(specs.get("execution"))
