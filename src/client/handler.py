from client.parser import JsonParser
from client.relation import Relation
from client.rule import Rule
from nfqueue.constraint_mapping import MappingEntry
from nfqueue.handling_queue import HandlingQueue
from nft.nftables_api import NftablesAPI


class Handler:
    def __init__(self, handling_queue: HandlingQueue):
        self.nf_api = NftablesAPI()
        self.constraint_mapping = handling_queue.constraint_mapping
        self.packet_handler = handling_queue.packet_handler
        self.categorization = {}
        self.members = {}
        self.relations = {}
        self.triggers = []
        self.inferences = []
        self.inconsistencies = []
        self.mark = 0
        self.nf_api.init_ruleset()

    def add_rule(self, src, dst):
        is_ip6 = src.is_ip6

        handle = self.nf_api.add_rule(src.ip, src.port, dst.ip, dst.port, self.mark, is_ip6)
        forward_rule = Rule(src, dst, handle)
        handle = self.nf_api.add_rule(dst.ip, dst.port, src.ip, src.port, self.mark, is_ip6)
        backward_rule = Rule(dst, src, handle)

        return [forward_rule, backward_rule]

    def add_relation(self, name, relation):
        subject = relation["subject"]
        broker = relation["broker"]
        pub = relation["publisher"]
        sub = relation["subscriber"]
        constraints = relation["constraints"]

        if broker:
            first = self.add_rule(pub, broker)
            second = self.add_rule(broker, sub)

            relation = Relation(subject=subject, mark=self.mark, first=first,
                                second=second,
                                constraints=constraints)
        else:
            first = self.add_rule(pub, sub)
            relation = Relation(subject=subject, mark=self.mark, first=first,
                                constraints=constraints)

        mapping_entry = MappingEntry(subject, constraints)
        self.constraint_mapping.add_mapping(self.mark, mapping_entry)
        self.relations[name] = relation
        self.mark += 1

    def add_parser(self, parser: JsonParser):
        self.categorization = parser.parsed_categorization
        self.members = parser.parsed_members
        for name, relation in parser.parsed_relations.items():
            self.add_relation(name, relation)
        self.triggers = parser.parsed_triggers
        self.inferences = parser.parsed_inferences
        self.inconsistencies = parser.parsed_inconsistencies

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
                self.nf_api.enable_rule(handle)
            else:
                self.nf_api.disable_rule(handle)

    def enable_relation(self, key):
        self.enable_disable(key, True)

    def disable_relation(self, key):
        self.enable_disable(key, False)

    def revert_relation_mapping(self):
        revert_mapping = {}
        for key, relation in self.relations.items():
            revert_mapping[relation.mark] = relation
        return revert_mapping
