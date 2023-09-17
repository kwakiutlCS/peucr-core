import requests
from requests.auth import HTTPBasicAuth
import time
import sys


def verify_field(response, field):
    if not field:
        return {"valid": False, "msg": ""}

    json = response.json()

    key = field.get("field")
    value = field.get("value")

    if not json.get(key):
        msg = "Expected {} to be {}, but it is not present. ".format(key, value)
    else:
        if value == json.get(key):
            return {"valid": True}

        msg = "Expected {} to be {}, but got {}. ".format(key, value, json.get(key))

    return {"valid": False, "msg": msg}


def verify_fields(response, fields):
    msgs = ""

    for field in fields:
        verification = verify_field(response, field)
        if verification["valid"]:
            return verification

        msgs += verification["msg"]

    return {"valid": False, "msg": msgs}


def verify_code(response, codes):
    if not codes:
        return {"valid": False, "msg": ""}

    success = response.status_code in codes

    return {"valid": success, "msg": None if success else "Expected status code to be one of {}, but got {}. ".format(codes, response.status_code)}


def verify_response(response, code, field):
    codeVerification = verify_code(response, code)
    if codeVerification["valid"]:
        return {"valid": True}

    fieldVerification = verify_fields(response, field)
    if fieldVerification["valid"]:
        return {"valid": True}

    return {"valid": False, "msg": "Failure. {}{}".format(codeVerification["msg"], fieldVerification["msg"])}


def exec_test(spec):
    print("Executing test \"{}\"".format(spec["name"]))

    actions = spec["actions"]
    if len(actions) == 0:
        print("No action was specified")
        return False

    # action
    for action in actions:
        executed = False
        startTime = time.time()

        while not executed and time.time() - startTime < 3:
            r = requests.post(action["url"], json=action["body"])
            executed = r.status_code == 200
            time.sleep(0.2)

    if not executed:
        print("Action failed. Validation will not be executed")
        return False

    # validation
    target = spec["validation"]["target"]
    fields = spec["validation"].get("fields")
    statusCodes = spec["validation"].get("status-codes")
    wait = spec["validation"].get("wait") if spec["validation"].get("wait") else 0
    duration = spec["validation"].get("duration") if spec["validation"].get("duration") else 5

    auth = None
    if target.get("username") is not None:
        auth = HTTPBasicAuth(target["username"], target["password"])
    headers = target.get("headers")

    time.sleep(wait)

    startTime = time.time()
    result = {"valid": False}
    while not result["valid"] and time.time() - startTime < duration:
        try:
            response = requests.get(target["url"], headers=headers, auth=auth)
            result = verify_response(response, statusCodes, fields)
        except Exception as e:
            result["msg"] = "Error:", e

        time.sleep(0.2)

    if not result["valid"]:
        print(result["msg"])

    return result["valid"]


def exec_test_suite(specs):
    successes = 0

    for spec in specs:
        print("*********************")
        if exec_test(spec):
            print("SUCCESS")
            successes += 1

    print("*********************")

    if successes != len(specs):
        print(len(specs), "tests run", len(specs) - successes, "failures")
        sys.exit(1)        

    print(len(specs), "tests run. No failures.")



def verify_preconditions(validations, plugins):
    print("*********************")
    print("Executing preconditions")

    for validation in validations:
        print("Verifying", validation["name"])
        executablePlugins = [p for p in plugins if p.executes(validation["name"])]

        if len(executablePlugins) == 0:
            print("No plugin was found for", validation["name"], "precondition")
            sys.exit(1)

        plugin = executablePlugins[0]

        fields = validation.get("fields")
        statusCodes = validation.get("status-codes")

        startTime = time.time()
        result = {"valid": False}
        while not result["valid"] and time.time() - startTime < 2:
            try:
                response = plugin.apply()
                result = verify_response(response, statusCodes, fields)
            except Exception as e:
                time.sleep(0.2)
         
        if not result["valid"]:
            print("Precondition validation failed. Test will be aborted")
            print("*********************")
            sys.exit(1)

    print("Preconditions confirmed. Test will start")
    print("*********************")
    time.sleep(1)
