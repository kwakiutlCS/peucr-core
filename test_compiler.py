def compile_body(action):
    if action.get("body") is not None:
        return { "content": action["body"] }
        
    if action["action"] == "UNBLOCK" and action.get("gcid") is not None:
        return {
            "content":"{\"AccountActivation\":{\"gcid\":\"" + action["gcid"] + "\"}}"        
        }

    if action["action"] == "BLOCK" and action.get("gcid") is not None:
        return {
            "content":"{\"AccountDeletion\":{\"gcid\":\"" + action["gcid"] + "\"}}"        
        }


def compile_action(action, config):
    return {"url": config["urlbroker"] + ("/blockUser" if action["action"] == "BLOCK" else "/unblockUser"),
            "body": compile_body(action)}


def compile_actions(actions, config):
    return [compile_action(action, config) for action in actions]


def compile_validation(validation, config):
    target = None
    if validation["target"] == "DPP-BLOCKED":
        target = {"url": config["urldpp"],
                  "username": config["username"],
                  "password": config["password"],
                  "headers": {"X-rgw-gcid": validation["gcid"],
                              "accept": "application/json"}
                  }
        
    compiled = {"target": target, "name": validation["target"], "fields": []}

    expectations = validation["expectation"]

    if expectations.get("status-code"):
        compiled["status-codes"] = [expectations["status-code"]]
    elif expectations.get("field"):
        compiled["fields"] = [{"field": expectations["field"], "value": expectations["value"]}]
    elif expectations.get("one-of"):
        compiled["fields"] = [e for e in expectations.get("one-of") if e.get("field")]
        compiled["status-codes"] = [e["status-code"] for e in expectations.get("one-of") if e.get("status-code")]

    if validation.get("wait"):
        compiled["wait"] = validation["wait"]
        compiled["duration"] = 1

    return compiled


def compile_spec(spec, config):
    return {"name": spec["name"], "actions": compile_actions(spec["actions"], config), "validation": compile_validation(spec["validation"], config)}


def compile_specs(specs, config):
    return [compile_spec(spec, config) for spec in specs]


def compile_preconditions(preconditions, config):
    validations = [compile_validation(precondition, config) for precondition in preconditions]

    return [v for v in validations if v is not None]
