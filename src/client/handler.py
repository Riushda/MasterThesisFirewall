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
        self.packet_signatures = {}
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
            signature = pub.ip + broker.ip + sub.ip
        else:
            signature = pub.ip + sub.ip

        if signature in self.packet_signatures:
            mark = self.packet_signatures[signature]
            for relation_keys, relation in self.relations.items():
                if relation.mark == mark:
                    new_relation = Relation(subject=subject, mark=mark, first=relation.first,
                                            second=relation.second,
                                            constraints=constraints, time_intervals=time_intervals)
                    self.relations[name] = new_relation
                    break
            self.relation_mapping.add_relation(mark, RelationEntry(subject, constraints))
        else:
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

            self.relation_mapping.add_relation(self.mark, RelationEntry(subject, constraints))
            self.relations[name] = relation
            self.packet_signatures[signature] = self.mark
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

    def revert_relation_mapping(self):
        revert_mapping = {}
        for key, relation in self.relations.items():
            revert_mapping[relation.mark] = relation
        return revert_mapping
