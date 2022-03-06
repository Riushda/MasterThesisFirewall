import nftables
import json
import os
from .utils import *
from constant import *


class NftablesAPI:
    def __init__(self):
        nft = nftables.Nftables()
        nft.set_json_output(True)

        # important! to get the rule handle when getting the ruleset
        nft.set_handle_output(
            True
        )

        self.nft = nft
        self.dirname = os.path.dirname(__file__)

    def init_ruleset(self):
        cmd = json.load(open(f"{self.dirname}/patterns/init_ruleset.json"))
        self.send_command(cmd)

    def send_command(self, json_order):

        try:
            self.nft.json_validate(json_order)
        except Exception as e:
            print(f"ERROR: failed validating JSON schema: {e}")
            exit(1)

        rc, output, error = self.nft.json_cmd(json_order)
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
        else:
            if len(output) != 0:
                # more error control?
                print(f"WARNING: output: {output}")

        return output

    def add_rule(self, src=None, sport=None, dst=None, dport=None, policy=POLICY_JSON.DEFAULT.value):

        # build the json rule command

        add_rule = json.load(open(f"{self.dirname}/patterns/add_rule.json"))

        if src:
            set_json_ip(add_rule, src, "saddr")

        if dst:
            set_json_ip(add_rule, dst, "daddr")

        if sport:
            set_json_port(add_rule, sport, "sport")

        if dport:
            set_json_port(add_rule, dport, "dport")

        add_rule["nftables"][0]["add"]["rule"]["expr"].append(policy)

        self.send_command(add_rule)

        # find the rule in nftables

        # get the rules in the chain
        rule_list = self.send_command(
            json.load(open(f"{self.dirname}/patterns/list_chain.json")))

        rule = last_rule_index(rule_list)  # get the rule

        # create mark and append it to the rule

        mark = json.load(open(f"{self.dirname}/patterns/mark.json"))
        # set the mark as the index of the rule
        mark["mangle"]["value"] = rule["handle"]

        rule["expr"] = rule["expr"][:-1]
        rule["expr"].append(mark)
        rule["expr"].append(policy)

        # replace the rule in nftables

        update_rule = {"nftables": [{"replace": {"rule": rule}}]}

        self.send_command(update_rule)

        return rule["handle"]

    def del_rule(self, handle):
        del_rule = json.load(open(f"{self.dirname}/patterns/delete_rule.json"))

        del_rule["nftables"][0]["delete"]["rule"]["handle"] = handle

        self.send_command(del_rule)

    def enable_rule(self, handle, policy=POLICY_JSON.DEFAULT.value):
        rule_list = self.send_command(
            json.load(open(f"{self.dirname}/patterns/list_chain.json")))
        rule = get_rule(rule_list, handle)

        rule["expr"].pop()
        rule["expr"].append(policy)

        update_rule = {"nftables": [{"replace": {"rule": rule}}]}
        self.send_command(update_rule)

    def disable_rule(self, handle):
        rule_list = self.send_command(
            json.load(open(f"{self.dirname}/patterns/list_chain.json")))
        rule = get_rule(rule_list, handle)

        rule["expr"].pop()

        rule["expr"].append({
            "jump": {
                "target": "DISABLE"
            }
        })

        update_rule = {"nftables": [{"replace": {"rule": rule}}]}
        self.send_command(update_rule)

    def list_ruleset(self):
        cmd = json.load(open(f"{self.dirname}/patterns/list_ruleset.json"))
        print(json.dumps(self.send_command(cmd), indent=4, sort_keys=True))

    def flush_ruleset(self):
        cmd = json.load(open(f"{self.dirname}/patterns/flush_ruleset.json"))
        self.send_command(cmd)
