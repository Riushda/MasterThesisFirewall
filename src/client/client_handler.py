import threading

import Pyro4
import schedule

from client.constraint import parse_constraints
from client.member import Member, parse_member
from client.schedule_thread import ScheduleThread
from client.utils import add_with_broker, add_without_broker
from nft.nftables_api import NftablesAPI
from utils.constant import *

api = NftablesAPI()
api.init_ruleset()

s_mutex = threading.Lock()
schedule_thread = ScheduleThread(s_mutex, schedule)
schedule_thread.start()


def stop_client_handler():
    schedule_thread.stop()
    api.flush_ruleset()


class Handler(object):
    def __init__(self, mapping, packet_handler, pub_list, sub_list, broker_list, relations):
        self.constraint_mapping = mapping
        self.packet_handler = packet_handler
        self.api = api
        self.schedule = schedule
        self.pub_list = pub_list
        self.sub_list = sub_list
        self.broker_list = broker_list
        self.relations = relations
        self.current_mark = 0

    @Pyro4.expose
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

    @Pyro4.expose
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

    @Pyro4.expose
    def add_relation(self, pub: str, sub: str, broker: str, policy: Policy, subject: str, constraints: list):

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

        parsed_constraints = parse_constraints(constraints)
        if not isinstance(parsed_constraints, list):
            return parsed_constraints

        if broker:
            if broker in self.broker_list:
                broker_member = self.broker_list[broker]
            else:
                broker_member = parse_member("dev", broker)
                if not isinstance(broker_member, Member):
                    return broker_member
            add_with_broker(self, pub_member, sub_member, broker_member, policy, subject, parsed_constraints)
        else:
            add_without_broker(self, pub_member, sub_member, policy, subject, parsed_constraints)

        return "Relation added!"

    @Pyro4.expose
    def remove_relation(self, index: int):

        if index >= len(self.relations):
            return "Error: This relation does not exist."

        found_relation = self.relations[index]

        rule_handle = found_relation.first.handle
        self.api.del_rule(rule_handle)
        mark = found_relation.mark
        self.constraint_mapping.del_mapping(str(mark))

        if found_relation.second:
            rule_handle = found_relation.second.handle
            self.api.del_rule(rule_handle)

        found_relation.cancel_jobs(self.schedule)
        del self.relations[index]

        return "Relation removed!"

    @Pyro4.expose
    def enable_relation(self, index: int):

        if index >= len(self.relations):
            return "Error: This relation does not exist."

        found_relation = self.relations[index]

        rule_handle = found_relation.first.handle
        self.api.enable_rule(rule_handle)

        if found_relation.second:
            rule_handle = found_relation.second.handle
            self.api.enable_rule(rule_handle)

        # found_relation.add_jobs(self.api, self.schedule, schedule_job)
        return "Relation enabled!"

    @Pyro4.expose
    def disable_relation(self, index: int):

        if index >= len(self.relations):
            return "Error: This relation does not exist."

        found_relation = self.relations[index]

        rule_handle = found_relation.first.handle
        self.api.disable_rule(rule_handle)

        if found_relation.second:
            rule_handle = found_relation.second.handle
            self.api.disable_rule(rule_handle)

        # found_relation.cancel_jobs(self.schedule)
        return "Relation disabled!"