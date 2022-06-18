"""
The handler communicates with the Nft API and modifies the Nftables ruleset, it is also responsible for building the
rules and the relations with the different members.
"""

from client.parser import Parser
from client.relation import Relation, Rule
from nfqueue.handling_queue import HandlingQueue
from nfqueue.relation_mapping import Relation as RelationEntry
from nfqueue.relation_mapping import RelationMapping
from nft.api import NftAPI


class Handler:
    def __init__(self, handling_queue: HandlingQueue, relation_mapping: RelationMapping, dev: bool):
        self.nft_api = NftAPI()
        self.relation_mapping = relation_mapping
        self.packet_handler = handling_queue.packet_handler
        self.categorization = {}
        self.members = {}
        self.relations = {}
        self.triggers = []
        self.inferences = []
        self.inconsistencies = []
        self.time_intervals = {}
        self.mark = 0
        self.signatures = {}
        self.nft_api.init_ruleset(dev)

    def add_rule(self, src, dst):
        is_ip6 = src.is_ip6
        handle = self.nft_api.add_rule(src.ip, src.port, dst.ip, dst.port, self.mark, is_ip6)
        forward_rule = Rule(src, dst, handle, self.mark)
        handle = self.nft_api.add_rule(dst.ip, dst.port, src.ip, src.port, self.mark, is_ip6)
        backward_rule = Rule(dst, src, handle, self.mark)
        return [forward_rule, backward_rule]

    def add_signature(self, src, dst, entry):
        signature = src.ip + src.str_port + dst.ip + dst.str_port
        if signature in self.signatures:
            rule = self.signatures[signature]
            self.relation_mapping.add_relation(rule[0].mark, entry)
        else:
            rule = self.add_rule(src, dst)
            self.signatures[signature] = rule
            self.relation_mapping.add_relation(self.mark, entry)
            self.mark += 1
        return rule

    def add_relation(self, name, relation):
        subject = relation["subject"]
        broker = relation["broker"]
        pub = relation["publisher"]
        sub = relation["subscriber"]
        constraints = relation["constraints"]
        time_intervals = relation["time_intervals"]

        second = None

        if broker:
            first = self.add_signature(pub, broker, RelationEntry(subject, constraints))
            second = self.add_signature(broker, sub, RelationEntry(subject, constraints))
        else:
            first = self.add_signature(pub, sub, RelationEntry(subject, constraints))

        relation = Relation(subject=subject, first=first,
                            second=second,
                            constraints=constraints, time_intervals=time_intervals)
        self.relations[name] = relation

    def add_parser(self, parser: Parser):
        self.categorization = parser.parsed_categorization
        self.members = parser.parsed_members
        for name, relation in parser.parsed_relations.items():
            self.add_relation(name, relation)
        self.triggers = parser.parsed_triggers
        self.inferences = parser.parsed_inferences
        self.inconsistencies = parser.parsed_inconsistencies
        self.time_intervals = parser.parsed_time_intervals
