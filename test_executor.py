import sys
from test_framework import TestFramework
from test_spec_loader import SpecLoader
from test_plugin_loader import PluginLoader
from test_config_loader import ConfigLoader


if __name__ == "__main__":
    config = ConfigLoader().apply(sys.argv)
    specs = SpecLoader().apply(config["specs"])
    plugins = PluginLoader().apply(config["plugins"])
    plugins = [plugin(config) for plugin in plugins]

    framework = TestFramework(plugins)
    framework.exec_preconditions(specs.get("preconditions"))
    framework.exec_test_suite(specs.get("execution"))
