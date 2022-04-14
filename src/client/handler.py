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

    def add_rule(self, src, dst):
        handle = self.nf_api.add_rule(src.ip, src.port, dst.ip, dst.port, self.mark)
        forward_rule = Rule(src, dst, handle)
        handle = self.nf_api.add_rule(dst.ip, dst.port, src.ip, src.port, self.mark)
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
            second = self.add_rule(broker, pub)

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
