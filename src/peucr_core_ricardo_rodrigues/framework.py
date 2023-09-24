import time
import sys
from peucr_core_ricardo_rodrigues.loaders import ConfigLoader, SpecLoader, PluginLoader


class TestFramework:
    def __init__(self, args):
        self.separator = "**************************************************"
        self.config = ConfigLoader(args).apply()
        self.specs = SpecLoader(self.config).apply()
        self.plugins = PluginLoader(self.config).apply()



    def verify_field(self, response, field):
        if not field:
            return {"valid": False, "msg": ""}

        entity = response["entity"]

        key = field.get("field")
        value = field.get("value")

        if not entity.get(key):
            msg = "Expected {} to be {}, but it is not present. ".format(key, value)
        else:
            if value == entity.get(key):
                return {"valid": True}

            msg = "Expected {} to be {}, but got {}. ".format(key, value, entity.get(key))

        return {"valid": False, "msg": msg}



    def verify_code(self, response, code):
        success = response["status"] == code

        return {"valid": success, "msg": None if success else "Expected status code to be {}, but got {}. ".format(code, response["status"])}



    def verify_response(self, expectation, response):
        if expectation is None:
            return {"valid": response["success"], "msg": ""}

        if expectation.get("status"):
            return self.verify_code(response, expectation.get("status"))

        if expectation.get("field"):
            return self.verify_field(response, expectation)

        msg = ""
        if expectation.get("one-of"):
            for one in expectation["one-of"]:
                verification = self.verify_response(one, response)
                if verification["valid"]:
                    return verification
                msg += verification["msg"]
                
        return {"valid": False, "msg": "{}".format(msg)}



    def get_plugin(self, name):
        executablePlugins = [p for p in self.plugins["custom"] if p.executes(name)]
        
        if len(executablePlugins) > 0:
            return executablePlugins[0]

        executablePlugins = [p for p in self.plugins["default"] if p.executes(name)]
        
        if len(executablePlugins) > 0:
            return executablePlugins[0]

        raise Exception("No plugin was found for", name)



    def exec_actions(self, actions):
        if actions is None or len(actions) == 0:
            return True

        for action in actions:
            plugin = self.get_plugin(action["target"])

            executed = False
            startTime = time.time()
            options = action["options"] if action.get("options") else {}

            while not executed and time.time() - startTime < 3:
                r = plugin.apply(options)
                executed = r["success"]
                time.sleep(0.2)

        if not executed:
            print("Action failed. Validation will not be executed")
            return False

        return True



    def exec_validation(self, validation):
        plugin = self.get_plugin(validation["target"])

        options = validation.get("options")
        wait = validation.get("wait") if validation.get("wait") else 0
        duration = 1 if validation.get("wait") else 5
        expectation = validation.get("expectation")

        time.sleep(wait)

        startTime = time.time()
        result = {"valid": False}
        while not result["valid"] and time.time() - startTime < duration:
            try:
                response = plugin.apply(options)
                result = self.verify_response(expectation, response)
            except Exception as e:
                result["msg"] = "Error:", e

            time.sleep(0.2)

        if not result["valid"]:
            print("Failure.", result["msg"])

        return result["valid"]



    def exec_validations(self, validations):
        if not validations or len(validations) == 0:
            print("No validation specified in test. Aborting.")
            return False

        for validation in validations:
            if not self.exec_validation(validation):
                return False

        return True



    def exec_test(self, spec):
        print("Executing test \"{}\"".format(spec["name"] if spec.get("name") else "UNNAMED"))

        if not self.exec_actions(spec.get("context")):
            return False

        if not self.exec_actions(spec.get("actions")):
            return False

        return self.exec_validations(spec.get("validation"))



    def exec_test_suite(self, specs):
        successes = 0

        for spec in specs:
            if self.exec_test(spec):
                successes += 1

        print(self.separator)

        if successes != len(specs):
            print(len(specs), "tests run", len(specs) - successes, "failures")
            sys.exit(1)        

        print(len(specs), "tests run. No failures.")



    def exec_preconditions(self, validations):
        if validations is None or validations.get("validation") is None:
            return

        for validation in validations["validation"]:
            print("Verifying", (validation["name"] if validation.get("name") else "UNNAMED"))
            if not self.exec_validation(validation):
                print("Precondition validation failed. Test will be aborted")
                print(self.separator)
                sys.exit(1)

        print("Preconditions confirmed. Test will start")
        print(self.separator)



    def exec(self):
        self.exec_preconditions(self.specs.get("preconditions"))
        self.exec_test_suite(self.specs.get("execution"))