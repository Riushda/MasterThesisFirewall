import nftables
import json

from nftables_pattern import *

def get_rule_index(list, rule):
    index = 0
    for element in list:
        if "rule" in element :
            element = element["rule"]

            if rule.items() <= element.items() :
                index = element["handle"]
                break

    return index

def add_rule(nft, sport = None, dport = None, dst = None, src = None):

    # build the json rule command

    add_rule = NFTABLES_ADD_RULE.copy()

    if sport != None :
        sport_json = NFTABLES_PORT_MATCHING.copy()
        sport_json[1]["match"]["right"] = sport
        add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, sport_json[0])
        add_rule["nftables"][0]["add"]["rule"]["expr"].insert(1, sport_json[1])
    
    if dport != None :
        dport_json = NFTABLES_PORT_MATCHING.copy()
        dport_json[1]["match"]["right"] = dport
        add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, dport_json[0])
        add_rule["nftables"][0]["add"]["rule"]["expr"].insert(1, dport_json[1])

    send_command(nft, add_rule) # add the rule

    list_rules = NFTABLES_LIST_CHAIN.copy()
    output = send_command(nft, list_rules) # get the rules in the chain

    rule = NFTABLES_ADD_RULE["nftables"][0]["add"]["rule"].copy()
    index = get_rule_index(output, rule) # get the index of the rule
    
    mark = NFTABLES_MARK.copy()
    mark["mangle"]["value"] = index
    update_rule = add_rule
    update_rule["nftables"][0]["add"]["rule"]["expr"][:-1]
    update_rule["nftables"][0]["replace"] = update_rule["nftables"][0].pop("add")
    update_rule["nftables"][0]["replace"]["rule"]["expr"].append(mark)
    update_rule["nftables"][0]["replace"]["rule"]["handle"] = index
    update_rule["nftables"][0]["replace"]["rule"]["expr"].append({"accept" : None})
    print(update_rule)
    send_command(nft, update_rule) # update the rule with the mark
    # DO NOT WORK BUT FIX IS EASY , DO NOT TOUCH PLEASE
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
    add_rule(nft, sport=80)
    

if __name__ == "__main__":
    main()