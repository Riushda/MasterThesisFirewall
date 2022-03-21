from network_context import NetworkContext
from network_context import DeviceState


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

        # add actions of rules in all transitions validating the conditions
        for state_src in self.network_context.states:
            for state_dst in self.network_context.states:
                state_src: DeviceState = state_src
                state_dst: DeviceState = state_dst

                if state_src.name != state_dst.name and state_src.is_consistent and state_dst.is_consistent:

                    changed_element = self.network_context.transitions_change.get((state_src.name, state_dst.name))
                    if changed_element:  # if transition between both states
                        changed_element = changed_element["change"]
                        changed_element_keys = list(changed_element.keys())

                        for rule in rules:
                            condition = rule["condition"]

                            condition_changed = False
                            for key in changed_element_keys:
                                if key in condition:
                                    condition_changed = True
                                    break

                            if condition_changed:
                                action = None

                                # if condition of rule does no longer hold
                                if condition.items() <= state_src.state.items():
                                    action = {"index": rule["index"], "reverse action": rule["action"]}

                                # if condition of rule now holds
                                if condition.items() <= state_dst.state.items():
                                    action = {"index": rule["index"], "action": rule["action"]}

                                if action:
                                    self.network_context.transitions_change[(state_src.name, state_dst.name)][
                                        "actions"].append(action)

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

        # delete actions of rules with index in rule_index in all transitions
        if len(rules_to_delete) > 0:
            for state_src in self.network_context.states:
                for state_dst in self.network_context.states:
                    state_src: DeviceState = state_src
                    state_dst: DeviceState = state_dst

                    if state_src != state_dst and state_src.is_consistent and state_dst.is_consistent:
                        changed_element = self.network_context.transitions_change.get((state_src.name, state_dst.name))
                        if changed_element:  # if transition between both states
                            for action in changed_element["actions"]:
                                for rule_to_delete in rules_to_delete:
                                    if action["index"] == rule_to_delete:
                                        changed_element["actions"].remove(action)
                                        break

        return rules_to_delete

    def del_rule(self, rule_index):
        deleted_indexes = self.del_multiple_rules([rule_index])

        if len(deleted_indexes) > 0:
            return deleted_indexes[0]
        else:
            return -1
