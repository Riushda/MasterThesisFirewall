from context.network import NetworkContext


class AbstractRule:
    def __init__(self, abstract_rules, network_context: NetworkContext):
        self.abstract_rules = {}
        self.network_context = network_context
        self.add_multiple_rules(abstract_rules)

    def add_multiple_rules(self, rules):
        # add rules in abstract_rules list
        for rule in rules:
            added = False
            index = 0
            while not added:
                if not self.abstract_rules.get(index):
                    rule["index"] = index
                    self.abstract_rules[index] = rule
                    added = True
                else:
                    index += 1

        self.network_context.add_rules(rules)

        return rules

    def add_rule(self, rule):
        rules = self.add_multiple_rules([rule])
        return rules[0]["index"]

    def del_multiple_rules(self, rule_indexes):
        # delete rules in abstract_rules
        rules_to_delete = []
        for rule_index in rule_indexes:
            deleted = self.abstract_rules.pop(rule_index, None)
            if deleted:
                rules_to_delete.append(rule_index)

        self.network_context.del_rules(rules_to_delete)

        return rules_to_delete

    def del_rule(self, rule_index):
        deleted_indexes = self.del_multiple_rules([rule_index])

        if len(deleted_indexes) > 0:
            return deleted_indexes[0]
        else:
            return -1
