import nftables

from nft.command_builder import *
from utils.constant import *


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

    def init_ruleset(self):
        builder = CommandBuilder()
        builder.init_ruleset()
        self.send_command(builder.get_command())

    def add_rule(self, src: str = None, sport: int = None, dst: str = None, dport: int = None, mark: int = 0):

        builder = CommandBuilder()
        builder.add_rule()
        builder.set_ip(src, "saddr")
        builder.set_ip(dst, "daddr")
        builder.set_port(sport, "sport")
        builder.set_port(dport, "dport")
        builder.set_mark(mark)
        builder.set_policy()

        self.send_command(builder.get_command())

        builder.list_chain()
        rule_list = self.send_command(builder.get_command())

        return last_rule_handle(rule_list)

    def del_rule(self, handle: int):
        builder = CommandBuilder()
        builder.delete_rule(handle)

        self.send_command(builder.get_command())

    def enable_rule(self, handle, policy: Policy = Policy.ACCEPT.value):
        builder = CommandBuilder()
        builder.list_chain()
        rule_list = self.send_command(builder.get_command())
        builder.set_command(get_rule(rule_list, handle))
        builder.enable_rule()
        self.send_command(builder.get_command())

    def disable_rule(self, handle):
        builder = CommandBuilder()
        builder.list_chain()
        rule_list = self.send_command(builder.get_command())
        builder.set_command(get_rule(rule_list, handle))
        builder.disable_rule()
        self.send_command(builder.get_command())

    def list_ruleset(self):
        builder = CommandBuilder()
        builder.list_ruleset()
        ruleset = self.send_command(builder.get_command())
        print(json.dumps(ruleset, indent=4, sort_keys=True))

    def flush_ruleset(self):
        builder = CommandBuilder()
        builder.flush_ruleset()
        self.send_command(builder.get_command())

    def store_ruleset(self):
        builder = CommandBuilder()
        builder.list_ruleset()
        ruleset = self.send_command(builder.get_command())
        file = open("nft/patterns/ruleset.json.json", "w")
        file.write(json.dumps(ruleset))

    def restore_ruleset(self):
        self.init_ruleset()
        builder = CommandBuilder()
        builder.restore_ruleset()
        print(json.dumps(builder.get_command(), indent=4, sort_keys=True))
        self.send_command(builder.get_command())