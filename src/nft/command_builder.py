import json

# TODO finish this class

class CommandBuilder():
    def __init__(self):
        pass

    def load_json(self, file):
        return json.load(open(f"./patterns/{file}.json"))

    def print_json(self, json):
        json.dumps(json, indent=4, sort_keys=True)

    def append_init(self, cmd):
        cmd["nftables"] = []

    def append_add(self, cmd):
        cmd["nftables"].append({"add":{}})

    def append_rule(self, cmd):
        pass
