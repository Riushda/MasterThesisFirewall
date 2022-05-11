from client.parser import Parser
from client.relation import Relation, Rule
from nfqueue.constraint_mapping import MappingEntry
from nfqueue.handling_queue import HandlingQueue
from nft.api import NftAPI


class Handler:
    def __init__(self, handling_queue: HandlingQueue, dev: bool):
        self.nft_api = NftAPI()
        self.constraint_mapping = handling_queue.constraint_mapping
        self.packet_handler = handling_queue.packet_handler
        self.categorization = {}
        self.members = {}
        self.relations = {}
        self.triggers = []
        self.inferences = []
        self.inconsistencies = []
        self.time_intervals = {}
        self.mark = 0
        self.nft_api.init_ruleset(dev)

    def add_rule(self, src, dst):
        is_ip6 = src.is_ip6

        handle = self.nft_api.add_rule(src.ip, src.port, dst.ip, dst.port, self.mark, is_ip6)
        forward_rule = Rule(src, dst, handle)
        handle = self.nft_api.add_rule(dst.ip, dst.port, src.ip, src.port, self.mark, is_ip6)
        backward_rule = Rule(dst, src, handle)

        return [forward_rule, backward_rule]

    def add_relation(self, name, relation):
        subject = relation["subject"]
        broker = relation["broker"]
        pub = relation["publisher"]
        sub = relation["subscriber"]
        constraints = relation["constraints"]
        time_intervals = relation["time_intervals"]

        if broker:
            first = self.add_rule(pub, broker)
            second = self.add_rule(broker, sub)

            relation = Relation(subject=subject, mark=self.mark, first=first,
                                second=second,
                                constraints=constraints, time_intervals=time_intervals)
        else:
            first = self.add_rule(pub, sub)
            relation = Relation(subject=subject, mark=self.mark, first=first,
                                constraints=constraints, time_intervals=time_intervals)

        mapping_entry = MappingEntry(subject, constraints)
        self.constraint_mapping.add_mapping(self.mark, mapping_entry)
        self.relations[name] = relation
        self.mark += 1

    def add_parser(self, parser: Parser):
        self.categorization = parser.parsed_categorization
        self.members = parser.parsed_members
        for name, relation in parser.parsed_relations.items():
            self.add_relation(name, relation)
        self.triggers = parser.parsed_triggers
        self.inferences = parser.parsed_inferences
        self.inconsistencies = parser.parsed_inconsistencies
        self.time_intervals = parser.parsed_time_intervals

    def enable_disable(self, key, action):

        if key in self.relations:
            found_relation = self.relations[key]
        else:
            return

        handles = [found_relation.first[0].handle, found_relation.first[1].handle]

        if found_relation.second:
            handles.append(found_relation.second[0].handle)
            handles.append(found_relation.second[1].handle)

        for handle in handles:
            if action:
                self.nft_api.enable_rule(handle)
            else:
                self.nft_api.disable_rule(handle)

    def enable_relation(self, key):
        self.enable_disable(key, True)

    def disable_relation(self, key):
        self.enable_disable(key, False)

    def revert_relation_mapping(self):
        revert_mapping = {}
        for key, relation in self.relations.items():
            revert_mapping[relation.mark] = relation
        return revert_mapping
