import requests
import time
import sys


class TestFramework:
    def __init__(self, plugins, config):
        self.plugins = plugins
        self.config = config
        self.separator = "**************************"
        
    def verify_field(self, response, field):
        if not field:
            return {"valid": False, "msg": ""}

        fields = response["fields"]

        key = field.get("field")
        value = field.get("value")

        if not fields.get(key):
            msg = "Expected {} to be {}, but it is not present. ".format(key, value)
        else:
            if value == fields.get(key):
                return {"valid": True}

            msg = "Expected {} to be {}, but got {}. ".format(key, value, fields.get(key))

        return {"valid": False, "msg": msg}


    def verify_fields(self, response, fields):
        msgs = ""

        for field in fields:
            verification = self.verify_field(response, field)
            if verification["valid"]:
                return verification

            msgs += verification["msg"]

        return {"valid": False, "msg": msgs}


    def verify_code(self, response, codes):
        if not codes:
            return {"valid": False, "msg": ""}

        success = response["status-code"] in codes

        return {"valid": success, "msg": None if success else "Expected status code to be one of {}, but got {}. ".format(codes, response["status-code"])}


    def verify_response(self, response, code, field):
        codeVerification = self.verify_code(response, code)
        if codeVerification["valid"]:
            return {"valid": True}

        fieldVerification = self.verify_fields(response, field)
        if fieldVerification["valid"]:
            return {"valid": True}

        return {"valid": False, "msg": "Failure. {}{}".format(codeVerification["msg"], fieldVerification["msg"])}


    def exec_test(self, spec):
        print("Executing test \"{}\"".format(spec["name"]))

        actions = spec["actions"]
        if len(actions) == 0:
            print("No action was specified")
            return False

        # action
        for action in actions:
            name = action["action"]
            executablePlugins = [p for p in self.plugins if p.executes(name)]
            
            if len(executablePlugins) == 0:
                print("No plugin was found for", name)
                sys.exit(1)

            plugin = executablePlugins[0]

            executed = False
            startTime = time.time()
            options = action["options"] if action.get("options") else {}

            while not executed and time.time() - startTime < 3:
                r = plugin.apply(options)
                executed = r["status-code"] == 200
                time.sleep(0.2)

        if not executed:
            print("Action failed. Validation will not be executed")
            return False

        # validation
        name = spec["validation"]["name"]
        executablePlugins = [p for p in self.plugins if p.executes(name)]

        if len(executablePlugins) == 0:
            print("No plugin was found for", name)
            sys.exit(1)
            
        plugin = executablePlugins[0]
        fields = spec["validation"].get("fields")
        statusCodes = spec["validation"].get("status-codes")
        wait = spec["validation"].get("wait") if spec["validation"].get("wait") else 0
        duration = spec["validation"].get("duration") if spec["validation"].get("duration") else 5
        options = spec["validation"].get("options")

        time.sleep(wait)

        startTime = time.time()
        result = {"valid": False}
        while not result["valid"] and time.time() - startTime < duration:
            try:
                response = plugin.apply(options)
                result = self.verify_response(response, statusCodes, fields)
            except Exception as e:
                result["msg"] = "Error:", e

            time.sleep(0.2)

        if not result["valid"]:
            print(result["msg"])

        return result["valid"]


    def exec_test_suite(self, specs):
        successes = 0

        for spec in specs:
            print(self.separator)
            if self.exec_test(spec):
                print("SUCCESS")
                successes += 1

        print(self.separator)

        if successes != len(specs):
            print(len(specs), "tests run", len(specs) - successes, "failures")
            sys.exit(1)        

        print(len(specs), "tests run. No failures.")



    def verify_preconditions(self, validations):
        print(self.separator)
        print("Executing preconditions")

        for validation in validations:
            print("Verifying", validation["name"])
            executablePlugins = [p for p in self.plugins if p.executes(validation["name"])]

            if len(executablePlugins) == 0:
                print("No plugin was found for", validation["name"])
                sys.exit(1)

            plugin = executablePlugins[0]

            fields = validation.get("fields")
            statusCodes = validation.get("status-codes")

            startTime = time.time()
            result = {"valid": False}
            while not result["valid"] and time.time() - startTime < 2:
                try:
                    response = plugin.apply()
                    result = self.verify_response(response, statusCodes, fields)
                except Exception as e:
                    time.sleep(0.2)
             
            if not result["valid"]:
                print("Precondition validation failed. Test will be aborted")
                print(self.separator)
                sys.exit(1)

        print("Preconditions confirmed. Test will start")
        print(self.separator)
        time.sleep(1)
