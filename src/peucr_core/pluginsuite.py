from peucr_core.plugins.http import HttpPlugin
from peucr_core.plugins.sqs_purge import SqsPurge
from peucr_core.plugins.sqs_receive import SqsReceive
from peucr_core.plugins.sqs_send import SqsSend
from peucr_core.exceptions import InvalidDefinitionException


class PluginSuite:
    def __init__(self, custom, config):
        self.default = [HttpPlugin(config), SqsPurge(config), SqsReceive(config), SqsSend(config)]
        self.custom = custom

    def apply(self, action):
        if action is None or (action is not None and "target" not in action):
            raise InvalidDefinitionException("action should have \"target\" defined")

        plugin = self.getPlugin(action["target"])

        return plugin.apply(action.get("options", {}))
        

    def getPlugin(self, name):
        executablePlugins = [p for p in self.custom if p.executes(name)]
        if len(executablePlugins) > 0:
            return executablePlugins[0]

        executablePlugins = [p for p in self.default if p.executes(name)]
        if len(executablePlugins) > 0:
            return executablePlugins[0]

        raise Exception("No plugin was found for " + name + ".")
