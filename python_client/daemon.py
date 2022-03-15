import signal
import sys
import threading

import Pyro4
import schedule

from constant import *
from constraint import parse_context
from member import Member, parse_member
from nft.nftables_api import NftablesAPI
from relation import Relation
from rule import Rule
from scheduleThread import ScheduleThread, schedule_job

api = NftablesAPI()
api.init_ruleset()

s_mutex = threading.Lock()
schedule_tread = ScheduleThread(s_mutex, schedule)
schedule_tread.start()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    schedule_tread.stop()
    api.flush_ruleset()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@Pyro4.expose
class Handlers(object):
    def __init__(self):
        self.api = api
        self.relations = []
        self.broker_list = {}
        self.pub_list = {}
        self.sub_list = {}

    def add_member(self, name: str, src: str, m_type: MemberType):

        member = parse_member(name, src, m_type)

        if not isinstance(member, Member):
            return member

        match m_type:
            case MemberType.BROKER.value:
                if name in self.broker_list:
                    return "Error: This name is already taken."
                self.broker_list[name] = member
                return f"Broker {name} {member} added!"
            case MemberType.PUB.value:
                if name in self.pub_list:
                    return "Error: This name is already taken."
                self.pub_list[name] = member
                return f"Publisher {name} {member} added!"
            case MemberType.SUB.value:
                if name in self.sub_list:
                    return "Error: This name is already taken."
                self.sub_list[name] = member
                return f"Subscriber {name} {member} added!"
            case _:
                return "Error: Not a valid member type."

    def remove_member(self, name: str, m_type: MemberType):
        try:
            match m_type:
                case MemberType.BROKER.value:
                    del self.broker_list[name]
                    return f"Broker {name} removed!"
                case MemberType.PUB.value:
                    del self.pub_list[name]
                    return f"Publisher {name} removed!"
                case MemberType.SUB.value:
                    del self.sub_list[name]
                    return f"Subscriber {name} removed!"
                case _:
                    return "Error: Not a valid member type."
        except KeyError:
            return "Error: This member does not exist."

    def add_relation(self, pub: str, sub: str, broker: str, policy: Policy, context: str):

        if not pub or not sub:
            return "Error: Please specify a publisher and a subscriber."

        if pub in self.pub_list:
            pub_member = self.pub_list[pub]
        else:
            pub_member = parse_member("dev", pub)
            if not isinstance(pub_member, Member):
                return pub_member

        if sub in self.sub_list:
            sub_member = self.sub_list[sub]
        else:
            sub_member = parse_member("dev", sub)
            if not isinstance(sub_member, Member):
                return sub_member

        constraints = parse_context(context)
        if not isinstance(constraints, list):
            return constraints

        if broker:
            if broker in self.broker_list:
                broker_member = self.broker_list[broker]
            else:
                broker_member = parse_member("dev", broker)
                if not isinstance(broker_member, Member):
                    return broker_member
            self.add_with_broker(pub_member, sub_member, broker_member, policy, constraints)
        else:
            self.add_without_broker(pub_member, sub_member, policy, constraints)

        return "Relation added!"

    def add_without_broker(self, pub: Member, sub: Member, policy, constraints):
        handle = api.add_rule(pub.ip, pub.port, sub.ip, sub.port,
                              PolicyJson[policy.upper()].value)
        rule = Rule(pub, sub, handle, policy)
        relation = Relation(rule, context=constraints)
        relation.add_jobs(api, schedule, schedule_job())
        self.relations.append(relation)

    def add_with_broker(self, pub: Member, sub: Member, broker: Member, policy, constraints):
        handle = api.add_rule(pub.ip, pub.port, broker.ip, broker.port,
                              PolicyJson[policy.upper()].value)
        first_rule = Rule(pub, broker, handle, policy)

        handle = api.add_rule(broker.ip, broker.port, sub.ip, sub.port,
                              PolicyJson[policy.upper()].value)
        second_rule = Rule(broker, sub, handle, policy)

        relation = Relation(
            first_rule, second_rule, context=constraints)
        self.relations.append(relation)

    def remove_relation(self, index: int):

        if index >= len(self.relations):
            return "Error: This relation does not exist."

        found_relation = self.relations[index]

        rule_handle = found_relation.first.handle
        api.del_rule(rule_handle)

        if found_relation.second:
            rule_handle = found_relation.second.handle
            api.del_rule(rule_handle)

        found_relation.cancel_jobs()
        del self.relations[index]

        return "Relation removed!"

    def show(self, table: str):

        result = ""

        if table == TableType.RELATIONS.value:
            for x in range(0, len(self.relations)):
                result += f"{x} | {self.relations[x]}\n"

        return result


daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Handlers())
ns.register("handlers", uri)
print("Daemon ready")
daemon.requestLoop()
