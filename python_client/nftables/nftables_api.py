import nftables
import json
from nftables_pattern import *

def get_rule_index(list, rule1, rule2):
    index = []
    for element in list:
        if "rule" in element :
            element = element["rule"]

            if rule1.items() <= element.items() :
                index.append(element["handle"])
            elif rule2!=None and rule2.items() <= element.items() :
                index.append(element["handle"])

    return index

def add_rule(nft):
    send_command(nft, NFTABLES_ADD_RULE)
    output = send_command(nft, NFTABLES_LIST_CHAIN)

    rule1 = NFTABLES_ADD_RULE["nftables"][0]["add"]["rule"]
    rule2 = NFTABLES_ADD_RULE["nftables"][1]["add"]["rule"]
    index = get_rule_index(output, rule1, rule2)

    return index

def del_rule():
    return 0

def enable_rule():
    return 0

def disable_rule():
    return 0

def send_command(nft, json_order):
    try:
        nft.json_validate(json_order)
    except Exception as e:
        print(f"ERROR: failed validating JSON schema: {e}")
        exit(1)

    rc, output, error = nft.json_cmd(json_order)
    if rc != 0:
        # do proper error handling here, exceptions etc
        print(f"ERROR: running JSON cmd: {error}")
        exit(1)

    if "list" in json_order["nftables"][0]:
        if len(output) == 0:
            # more error control
            print("ERROR: no output from libnftables")
            exit(0)
        return output["nftables"]
    else :
        if len(output) != 0:
            # more error control?
            print(f"WARNING: output: {output}")

    return output

def main():
    nft = nftables.Nftables()
    nft.set_json_output(True)
    nft.set_handle_output(
        True
    )  # important! to get the rule handle when getting the ruleset

    send_command(nft, NFTABLES_INIT)
    add_rule(nft)
    

if __name__ == "__main__":
    main()