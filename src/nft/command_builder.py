import json
import os

from utils.constant import *

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


def get_policy_json(policy: Policy):
    match policy:
        case Policy.ACCEPT.value:
            return load_json("accept_policy")
        case Policy.DROP.value:
            return load_json("drop_policy")


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

    def enable_rule(self, policy: Policy):
        self.command["expr"].pop()
        self.command["expr"].append(get_policy_json(policy))
        self.command = {"nftables": [{"replace": {"rule": self.command}}]}

    def disable_rule(self):
        self.command["expr"].pop()

        self.command["expr"].append(load_json("jump_disable"))

        self.command = {"nftables": [{"replace": {"rule": self.command}}]}

    def set_ip(self, ip, direction):
        if not ip:
            return
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

    def set_port(self, port: str, direction: str):
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

    def set_policy(self, policy: Policy):
        self.command["nftables"][0]["add"]["rule"]["expr"].append(get_policy_json(policy))

    def list_chain(self):
        self.command = load_json("list_chain")

    def list_ruleset(self):
        self.command = load_json("list_ruleset")

    def init_ruleset(self):
        self.command = load_json("init_ruleset")

    def flush_ruleset(self):
        self.command = load_json("flush_ruleset")

    def restore_ruleset(self):
        backup_ruleset = load_json("ruleset")
        self.command = {"nftables": []}
        for element in backup_ruleset[1:]:
            self.command["nftables"].append({"add": element})
