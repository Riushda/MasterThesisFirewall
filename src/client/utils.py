from client.member import Member
from client.relation import Relation
from client.rule import Rule
from client.schedule_thread import schedule_job
from nfqueue.constraint_mapping import MappingEntry
from utils.constant import *


def add_without_broker(handlers, pub: Member, sub: Member, policy: Policy, subject: str, constraints: list):
    mark = handlers.current_mark
    handle = handlers.api.add_rule(pub.ip, pub.port, sub.ip, sub.port, mark)
    rule = Rule(pub, sub, handle, policy)
    mapping_entry = MappingEntry(subject, constraints, policy)
    handlers.constraint_mapping.add_mapping(str(mark), mapping_entry)
    relation = Relation(rule, constraints=constraints, mark=str(mark), subject=subject)
    handlers.current_mark += 1
    relation.add_jobs(handlers.api, handlers.schedule, schedule_job)
    handlers.relations.append(relation)


def add_with_broker(handlers, pub: Member, sub: Member, broker: Member, policy: Policy, subject: str,
                    constraints: list):
    mark = handlers.current_mark
    handle = handlers.api.add_rule(pub.ip, pub.port, broker.ip, broker.port, mark)
    first_rule = Rule(pub, broker, handle, policy)

    handle = handlers.api.add_rule(broker.ip, broker.port, sub.ip, sub.port, mark)
    second_rule = Rule(broker, sub, handle, policy)

    mapping_entry = MappingEntry(subject, constraints, policy)
    handlers.constraint_mapping.add_mapping(str(mark), mapping_entry)
    relation = Relation(first_rule, second_rule, constraints=constraints, mark=str(mark), subject=subject)
    handlers.current_mark += 1
    relation.add_jobs(handlers.api, handlers.schedule, schedule_job)
    handlers.relations.append(relation)
