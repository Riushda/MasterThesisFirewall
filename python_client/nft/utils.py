import json
import os

dirname = os.path.dirname(__file__)


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


def set_json_port(add_rule, port, direction):
    port_json = json.load(open(f"{dirname}/patterns/port_matching.json"))

    port_json["match"]["left"]["payload"]["field"] = direction
    port_json["match"]["right"] = port

    add_rule["nftables"][0]["add"]["rule"]["expr"].append(port_json)


def set_json_ip(add_rule, ip, direction):
    ip_json = json.load(open(f"{dirname}/patterns/ip_matching.json"))

    ip_json["match"]["left"]["payload"]["field"] = direction

    ip_mask = ip.split("/")
    if len(ip_mask) > 1:  # if ip has mask
        ip_json["match"]["right"]["prefix"]["addr"] = ip_mask[0]  # set ip
        ip_json["match"]["right"]["prefix"]["len"] = int(
            ip_mask[1])  # set mask
    else:
        ip_json["match"]["right"] = ip_mask[0]  # set ip

    add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, ip_json)
