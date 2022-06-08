"""
This class provides a command constructor used to build the command sent to the Nftables daemon from the API.
"""

import json
import os

dirname = os.path.dirname(__file__)


def pattern_path(pattern: str):
    return f"{dirname}/patterns/{pattern}.json"


def load_json(pattern: str):
    return json.load(open(pattern_path(pattern)))


def last_rule_handle(rule_list):
    last_element = rule_list[len(rule_list) - 1]
    if "rule" in last_element:
        return last_element["rule"]["handle"]
    else:
        return 10


def get_rule(rule_list, handle):
    for element in rule_list:
        if "rule" in element and element["rule"]["handle"] == handle:
            return element["rule"]


class CommandBuilder:
    def __init__(self):
        self.command = []

    def set_command(self, command):
        self.command = command

    def get_command(self):
        return self.command

    def print_command(self):
        print(json.dumps(self.command, indent=4, sort_keys=True))

    def add_rule(self):
        self.command = load_json("add_rule")

    def delete_rule(self, handle: int):
        self.command = load_json("delete_rule")
        self.command["nftables"][0]["delete"]["rule"]["handle"] = handle

    def set_ip(self, ip, direction, is_ip6):
        if not ip:
            return

        if is_ip6:
            ip_json = load_json("ip6_matching")
        else:
            ip_json = load_json("ip_matching")

        ip_json["match"]["left"]["payload"]["field"] = direction

        ip_mask = ip.split("/")
        if len(ip_mask) > 1:  # if ip has mask
            ip_json["match"]["right"]["prefix"]["addr"] = ip_mask[0]  # set ip
            ip_json["match"]["right"]["prefix"]["len"] = int(
                ip_mask[1])  # set mask
        else:
            ip_json["match"]["right"] = ip_mask[0]  # set ip

        self.command["nftables"][0]["add"]["rule"]["expr"].insert(0, ip_json)

    def set_port(self, port: int, direction: str):
        if not port:
            return
        port_json = load_json("port_matching")

        port_json["match"]["left"]["payload"]["field"] = direction
        port_json["match"]["right"] = port

        self.command["nftables"][0]["add"]["rule"]["expr"].append(port_json)

    def set_mark(self, mark: int):
        mark_json = load_json("mark")
        mark_json["mangle"]["value"] = mark
        self.command["nftables"][0]["add"]["rule"]["expr"].append(mark_json)

    def set_policy(self):
        queue_json = load_json("queue_target")
        self.command["nftables"][0]["add"]["rule"]["expr"].append(queue_json)

    def list_chain(self):
        self.command = load_json("list_chain")

    def list_ruleset(self):
        self.command = load_json("list_ruleset")

    def init_ruleset(self, dev):
        self.command = load_json("init_ruleset")
        if not dev:
            for i in range(2, 5):
                self.command["nftables"][i]["add"]["chain"]["policy"] = "drop"

    def flush_ruleset(self):
        self.command = load_json("flush_ruleset")
