import sys

class ConfigLoader:

    def __init__(self):
        self.prefix = "--"


    def apply(self, args):
        if not self.get(args, "plugins") or not self.get(args, "specs"):
            print("--plugins and --specs flags are required")
            sys.exit(1)

        config = {}

        for index in range(len(args)):
            if self.is_flag(args, index):
                value = self.get(args, args[index])
                if value:
                    config[args[index][len(self.prefix):]] = value

        return config


    def get(self, args, name):
        flag = self.prefix + name if name[:2] != self.prefix else name

        if flag not in args:
            return None

        index = args.index(flag)

        if len(args) <= index+1 or self.is_flag(args, index+1):
            return None

        return args[index+1]


    def is_flag(self, args, index):
        return self.prefix == args[index][:2]
