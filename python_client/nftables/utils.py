import json


def last_rule_index(rule_list):
    for element in rule_list:
        if "rule" in element:
            return element["rule"]


def get_rule(rule_list, handle):
    for element in rule_list:
        if "rule" in element and element["rule"]["handle"] == handle:
            return element["rule"]


def set_json_port(add_rule, port, direction):
    port_json = json.load(open("./patterns/port_matching.json"))

    port_json["match"]["left"]["payload"]["field"] = direction
    port_json["match"]["right"] = port

    add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, port_json)


def set_json_ip(add_rule, ip, direction):
    ip_json = json.load(open("./patterns/ip_matching.json"))

    ip_json["match"]["left"]["payload"]["field"] = direction

    ip_mask = ip.split("/")
    if len(ip_mask) > 1:  # if ip has mask
        ip_json["match"]["right"]["prefix"]["addr"] = ip_mask[0]  # set ip
        ip_json["match"]["right"]["prefix"]["len"] = int(
            ip_mask[1])  # set mask
    else:
        ip_json["match"]["right"] = ip_mask[0]  # set ip

    add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, ip_json)