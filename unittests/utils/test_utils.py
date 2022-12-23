import json


def load_json(path):
    with open(path, encoding="UTF-8") as captured_json:
        return json.load(captured_json)
