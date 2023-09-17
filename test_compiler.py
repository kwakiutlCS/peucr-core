def compile_actions(actions, config):
    return actions


def compile_validation(validation, config):
    compiled = {"name": validation["target"], "fields": []}

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

    if validation.get("options"):
        compiled["options"] = validation["options"]

    return compiled


def compile_spec(spec, config):
    return {"name": spec["name"], "actions": spec["actions"], "validation": compile_validation(spec["validation"], config)}


def compile_specs(specs, config):
    return [compile_spec(spec, config) for spec in specs]


def compile_preconditions(preconditions, config):
    validations = [compile_validation(precondition, config) for precondition in preconditions]

    return [v for v in validations if v is not None]
