import nftables
import json
import copy
import ipaddress

from nftables_pattern import *

# return last rule added 
def get_rule_index(list):
    rule = None
    for element in list:
        if "rule" in element :
            rule = element["rule"]

    return rule

def set_json_port(add_rule, port, direction) :
    port_json = copy.deepcopy(NFTABLES_PORT_MATCHING)

    port_json["match"]["left"]["payload"]["field"] = direction
    port_json["match"]["right"] = port

    add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, port_json)

def set_json_ip(add_rule, ip, direction) :
    ip_json = copy.deepcopy(NFTABLES_IP_MATCHING)

    ip_json["match"]["left"]["payload"]["field"] = direction

    ip_mask = ip.split("/")
    if len(ip_mask)>1 : # if ip has mask
        ip_json["match"]["right"]["prefix"]["addr"] = ip_mask[0] # set ip
        ip_json["match"]["right"]["prefix"]["len"] = int(ip_mask[1]) # set mask 
    else :
        ip_json["match"]["right"] = ip_mask[0] # set ip

    add_rule["nftables"][0]["add"]["rule"]["expr"].insert(0, ip_json)

def add_rule(nft, src = None, sport = None, dst = None, dport = None ):

    # build the json rule command

    add_rule = copy.deepcopy(NFTABLES_ADD_RULE)

    if src!=None :
        set_json_ip(add_rule, src, "saddr")

    if dst!=None :
        set_json_ip(add_rule, dst, "daddr")

    if sport != None :
        set_json_port(add_rule, sport, "sport")
    
    if dport != None :
        set_json_port(add_rule, dport, "dport")
   
    send_command(nft, add_rule) # add the rule

    # find the rule in nftables
   
    list_rules = copy.deepcopy(NFTABLES_LIST_CHAIN)
    output = send_command(nft, list_rules) # get the rules in the chain

    rule = get_rule_index(output) # get the index of the rule

    # create mark and append it to the rule
    
    mark = copy.deepcopy(NFTABLES_MARK)
    mark["mangle"]["value"] = rule["handle"] # set the mark as the index of the rule

    rule["expr"] = rule["expr"][:-1]
    rule["expr"].append(mark)
    rule["expr"].append({"accept" : None})
    
    # replace the rule in nftables

    update_rule = add_rule
    update_rule["nftables"][0]["replace"] = update_rule["nftables"][0].pop("add")
    update_rule["nftables"][0]["replace"]["rule"] = rule

    send_command(nft, update_rule) 

    return rule["handle"]

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
    print(add_rule(nft, src="192.168.0.1/24", sport=80, dst="192.168.2.55/18", dport=22))
    print(add_rule(nft, src="192.168.0.1/25", sport=81, dst="192.168.2.55/19", dport=23))
    print(add_rule(nft, src="192.168.0.1/26", sport=82, dst="192.168.2.55/20", dport=24))
    print(add_rule(nft, src="192.168.0.1/26", sport=83, dst="192.168.2.55/21", dport=25))
    print(add_rule(nft, src="192.168.0.1/28", sport=84, dst="192.168.2.55/22", dport=26))
    

if __name__ == "__main__":
    main()