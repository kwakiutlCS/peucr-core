import os, json

class SpecLoader:

    def __init__(self):
        self.spec = "_spec.json"
        self.preconditions = "preconditions.json"

    def apply(self, path):
        specs = {}
        if self.spec in path:
            directory = "/".join(path.split("/")[:-1])
            files = os.listdir(directory)
            spec_files = [path.split("/")[-1]]
        else:
            directory = path
            files = os.listdir(directory)
            spec_files = [file for file in files if "_spec.json" in file]
            spec_files.sort()
        
        preconditions = directory+"/"+self.preconditions if self.preconditions in files else None

        if preconditions:
            with open(preconditions, "r") as p:
                specs["preconditions"] = json.loads(p.read())

        execution = []
        for file in spec_files:
            with open(directory+"/"+file, "r") as f:
                execution.append(json.loads(f.read()))

        specs["execution"] = execution

        return specs
