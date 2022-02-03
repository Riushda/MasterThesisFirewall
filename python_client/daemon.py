import Pyro4
import signal
import sys

from constant import *
from netlink import Netlink
from member import Member, parse_member
from relation import Relation
from rule import Rule
from constraint import parse_context

netlink = Netlink()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    netlink.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@Pyro4.expose
class Handlers(object):
    def __init__(self, netlink):
        self.netlink = netlink
        self.current_index = 0
        self.rules = []
        self.relations = []
        self.broker_list = {}
        self.pub_list = {}
        self.sub_list = {}

    def add_member(self, name, str_ip, str_port, type):

        member = parse_member(name, str_ip, str_port, type)

        if(not isinstance(member, Member)):
            return member

        match type:
            case M_TYPE.BROKER.value:
                if(name in self.broker_list):
                    return "This name is alreayd taken."
                self.broker_list[name] = member
                return f"Broker {name} {member} added!"
            case M_TYPE.PUB.value:
                if(name in self.pub_list):
                    return "This name is alreayd taken."
                self.pub_list[name] = member
                return f"Publisher {name} {member} added!"
            case M_TYPE.SUB.value:
                if(name in self.sub_list):
                    return "This name is alreayd taken."
                self.sub_list[name] = member
                return f"Subscriber {name} {member} added!"
            case _:
                return "Error: Not a valid member type."

    def remove_member(self, name, type):
        try:
            match type:
                case M_TYPE.BROKER.value:
                    del self.broker_list[name]
                    return f"Broker {name} removed!"
                case M_TYPE.PUB.value:
                    del self.pub_list[name]
                    return f"Publisher {name} removed!"
                case M_TYPE.SUB.value:
                    del self.sub_list[name]
                    return f"Subscriber {name} removed!"
                case _:
                    return "Error: Not a valid member type."
        except KeyError:
            return "Error: This member does not exist."

    def add_relation(self, pub, sub, broker, policy, context):

        constraints = parse_context(context)
        if(not isinstance(constraints, list)):
            return constraints

        try:
            pub_member = self.pub_list[pub]
            sub_member = self.sub_list[sub]

            broker_member = None
            if(broker != "/"):
                broker_member = self.broker_list[broker]
        except KeyError:
            return "Error: This member does not exist."

        if(broker_member):
            first_rule = Rule(
                pub_member, broker_member, self.current_index, policy)
            self.current_index += 1
            self.rules.append(first_rule)

            second_rule = Rule(
                broker_member, sub_member, self.current_index, policy)
            self.current_index += 1
            self.rules.append(second_rule)

            new_relation = Relation(
                first_rule, second_rule, context=constraints)
            self.relations.append(new_relation)
            print(new_relation.to_bytes())
        else:
            first_rule = Rule(
                pub_member, sub_member, self.current_index, policy)
            self.current_index += 1
            self.rules.append(first_rule)
            new_relation = Relation(first_rule, context=constraints)
            self.relations.append(new_relation)
            print(new_relation.to_bytes())

        return "Relation added!"

    def remove_relation(self, index):

        found_relation = None

        try:
            found_relation = self.relations[index]
        except IndexError:
            return "This relation does not exist."

        rule_index = found_relation.first.index

        del self.rules[rule_index]
        self.current_index -= 1

        offset = 1
        if(found_relation.second):
            del self.rules[rule_index]
            self.current_index -= 1
            offset += 1

        for x in range(rule_index, len(self.rules)):
            self.rules[x].index -= offset

        del self.relations[index]

        return "Relation removed!"

    def add_rule(self, src, sport, dst, dport, policy):

        src_member = parse_member("", src, sport, "")
        if(not isinstance(src_member, Member)):
            return src_member

        dst_member = parse_member("", dst, dport, "")
        if(not isinstance(dst_member, Member)):
            return dst_member

        new_rule = Rule(src_member, dst_member,
                        self.current_index, policy)

        self.current_index += 1
        self.rules.append(new_rule)

        return "Rule added!"

    def remove_rule(self, index):

        try:
            del self.rules[index]
        except IndexError:
            return "This rule does not exist."

        for x in range(index, len(self.rules)):
            self.rules[x].index -= 1

        return "Rule deleted!"

    def show_rules(self):
        result = ""

        for x in range(0, len(self.rules)):
            result += f"{self.rules[x].index} | {self.rules[x]}\n"

        return result

    def show_relations(self):

        result = ""

        for x in range(0, len(self.relations)):
            result += f"{x} | {self.relations[x]}\n"

        return result


daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Handlers(netlink))
ns.register("handlers", uri)
print("Daemon ready")
daemon.requestLoop()
