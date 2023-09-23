import os, sys
import inspect
import importlib

class PluginLoader:

    def __init__(self):
        self.plugin = "TestPlugin"


    def apply(self, path):
        if path[-1] == "/":
            path = path[0:-1]
        parentModule = path.split("/")[-1]

        plugins = []

        for file in os.listdir(path):
            try:
                lib = importlib.import_module(parentModule+"."+file.split(".")[0])
            except Exception as e:
                print(e)
                sys.exit(1)
                
            members = inspect.getmembers(lib, inspect.isclass)
            
            plugins.append(self.getTestPlugin(members, parentModule, lib))
            
        return [plugin for plugin in plugins if plugin is not None]

    
    def getTestPlugin(self, member, parent, lib):
        testClass = None
        testPlugin = False

        for clazz in member:
            if clazz[0] == self.plugin:
                testPlugin = True

            if parent+"." in str(clazz[1]):
                testClass = clazz[0]

        if testPlugin and testClass:
            return getattr(lib, testClass)
