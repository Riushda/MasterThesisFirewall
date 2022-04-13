from client.parser import JsonParser
from client.relation import Relation
from client.rule import Rule
from nfqueue.constraint_mapping import MappingEntry
from nft.nftables_api import NftablesAPI


class Handler:
    def __init__(self, constraint_mapping, packet_handler, labels, members, relations, context):
        self.nf_api = NftablesAPI()
        self.constraint_mapping = constraint_mapping
        self.packet_handler = packet_handler
        self.labels = labels
        self.members = members
        self.relations = relations
        self.context = context
        self.mark = 0
        self.nf_api.init_ruleset()

    def add_relation(self, name, relation):
        mark = self.mark
        subject = relation["subject"]
        broker = relation["broker"]
        pub = relation["publisher"]
        sub = relation["subscriber"]
        constraints = relation["constraints"]

        if broker:
            handle = self.nf_api.add_rule(pub.ip, pub.port, broker.ip, broker.port, mark)
            first_rule = Rule(pub, broker, handle)
            handle = self.nf_api.add_rule(broker.ip, broker.port, sub.ip, sub.port, mark)
            second_rule = Rule(broker, sub, handle)
            relation = Relation(subject=subject, mark=mark, first=first_rule, second=second_rule,
                                constraints=constraints)

        else:
            handle = self.nf_api.add_rule(pub.ip, pub.port, sub.ip, sub.port, mark)
            rule = Rule(pub, sub, handle)
            relation = Relation(subject=subject, mark=mark, first=rule,
                                constraints=constraints)

        mapping_entry = MappingEntry(subject, constraints)
        self.constraint_mapping.add_mapping(mark, mapping_entry)
        self.relations[name] = relation
        self.mark += 1

    def add_parser(self, parser: JsonParser):
        self.labels = parser.parsed_labels
        self.members = parser.parsed_members
        for name, relation in parser.parsed_relations.items():
            self.add_relation(name, relation)
        # for name, relation in self.relations.items():
        #    print(relation)
        self.context = parser.parsed_triggers

    def enable_relation(self, key):

        if key in self.relations:
            found_relation = self.relations[key]
        else:
            return

        first_handle = found_relation.first.handle
        self.nf_api.enable_rule(first_handle)

        if found_relation.second:
            second_handle = found_relation.second.handle
            self.nf_api.enable_rule(second_handle)

    def disable_relation(self, key):

        if key in self.relations:
            found_relation = self.relations[key]
        else:
            return

        first_handle = found_relation.first.handle
        self.nf_api.disable_rule(first_handle)

        if found_relation.second:
            second_handle = found_relation.second.handle
            self.nf_api.disable_rule(second_handle)

    def revert_relation_mapping(self):
        revert_mapping = {}
        for key, relation in self.relations.items():
            revert_mapping[relation.mark] = relation
        return revert_mapping
