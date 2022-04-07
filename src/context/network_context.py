import itertools as it

from transitions import Machine, State
from transitions.extensions import GraphMachine

from context.utils import get_device
import context.abstract_rule as abstract_rule


class DeviceState(State):
    def __init__(self, name, state, is_consistent):
        super().__init__(name, on_enter="enter", on_exit="exit")
        self.state = state
        self.is_consistent = is_consistent

    def __repr__(self):
        return str(self.state)

    def enter(self, event):
        if not self.is_consistent:
            print("Entering inconsistent state !")

    def exit(self, event):
        if not self.is_consistent:
            print("Leaving inconsistent state !")


class NetworkContext(object):
    def __init__(self, publisher_list, relations, initial_state, state_combinations, inconsistent_states,
                 state_inference):

        self.publisher_list = publisher_list
        self.relations = relations
        self.inconsistent_states = inconsistent_states
        self.state_inference = state_inference

        self.states = []
        self.transitions = []
        self.transitions_change = dict()

        self.machine: Machine = GraphMachine(None)

        # if self.check_inferences():
        self.build_fsm(initial_state, state_combinations)

    def build_fsm(self, initial_state, state_combinations):
        initial_state_name = ""
        i = 0
        # it.product is lazy, one combination is in memory at a given time
        for state_src in it.product(*(state_combinations[Name] for Name in state_combinations)):
            state_src = dict(zip(state_combinations.keys(), state_src))
            if state_src == initial_state:
                initial_state_name = str(i)

            is_src_consistent = self.is_consistent(state_src)
            self.states.append(DeviceState(str(i), state_src, is_src_consistent))

            j = 0
            for state_dst in it.product(*(state_combinations[Name] for Name in state_combinations)):
                state_dst = dict(zip(state_combinations.keys(), state_dst))

                key_trigger = None
                value_trigger = None

                # get all keys in state_src and state dst which doesn't have the same value
                diff_keys = [key for key in state_src.keys() & state_dst if state_src[key] != state_dst[key]]

                conforming = False

                # no state self loop and transition only between states with 1 difference
                if len(diff_keys) == 1:
                    infer = self.state_inference.get((diff_keys[0], state_dst[diff_keys[0]]))
                    if infer is None or state_dst[infer[0][0]] == infer[0][1]:
                        conforming = True

                        key_trigger = diff_keys[0]
                        value_trigger = state_dst[diff_keys[0]]

                        self.transitions_change[(str(i), str(j))] = {"change": {
                            diff_keys[0]: [state_src[diff_keys[0]], state_dst[diff_keys[0]]]},
                            "actions": []
                        }

                elif len(diff_keys) > 1:
                    for key in diff_keys:
                        infer = self.state_inference.get((key, state_dst[key]))

                        if infer:
                            diff = [element for element in diff_keys if element != key]
                            inferred_keys = [element[0] for element in infer]
                            conforming = set(diff).issubset(set(inferred_keys))

                            if conforming:
                                key_trigger = key
                                value_trigger = state_dst[key]

                                self.transitions_change[(str(i), str(j))] = {"change": {}, "actions": []}
                                for element in diff_keys:
                                    self.transitions_change[(str(i), str(j))]["change"][element] = [state_src[element],
                                                                                                    state_dst[element]]
                                break

                if conforming:
                    trigger = self.get_transition_trigger(key_trigger, value_trigger)

                    transition = {'trigger': trigger, 'source': str(i), 'dest': str(j), 'after': 'action'}
                    self.transitions.append(transition)

                j += 1

            i += 1

        self.machine = GraphMachine(model=self, states=self.states, transitions=self.transitions, initial=initial_state_name,
                               send_event=True)

    def draw_fsm(self):
        self.get_graph(title=str(self.current_state()), show_roi=True).draw('my_state_diagram.png', prog='dot')

    def is_consistent(self, state):
        for inconsistent in self.inconsistent_states:  # no forbidden state
            if inconsistent.items() <= state.items():
                return False

        return True

    def get_transition_trigger(self, key, value):
        return key + "=" + value

    def show_current_state(self):
        print(self.current_state())

    def current_state(self):
        return self.machine.get_state(self.state).state

    def is_current_state_consistent(self):
        return self.machine.get_state(self.state).is_consistent

    def action(self, event):
        # print("action: " + str(event))
        actions = self.transitions_change[(event.transition.source, event.transition.dest)]["actions"]

        for action in actions:
            print("action : " + str(action))
            abstract_rule.run_action(action)

    def self_loop(self, data):
        state = self.current_state()
        return state[data[0]] == data[1]

    # check that the inferences keys are publishers and that the values are the subscribers of their key
    def check_inferences(self):
        keys = self.state_inference.keys()

        for key in keys:
            device = get_device(key[0])

            # check if keys are publishers
            if device not in self.publisher_list:
                print(device + " : keys in inferences must be publishers !")
                return False

            # check if values are subscribers of their key
            values = self.state_inference[key]
            devices = []
            for value in values:
                devices.append(get_device(value[0]))

            for relation in self.relations:
                publisher = relation.first.src.name
                if publisher == device:

                    subscriber = None
                    if not relation.second:
                        subscriber = relation.first.dst.name
                    else:
                        subscriber = relation.second.dst.name

                    if subscriber in devices:
                        devices.remove(subscriber)

            if len(devices) > 0:
                print(str(devices) + " : devices values in inferences must be subscribers of their key !")
                return False

        return True

    def add_rules(self, rules):

        # add actions of rules in all transitions validating the conditions
        for state_src in self.states:
            for state_dst in self.states:
                state_src: DeviceState = state_src
                state_dst: DeviceState = state_dst

                if state_src.name != state_dst.name and state_src.is_consistent and state_dst.is_consistent:

                    changed_element = self.transitions_change.get((state_src.name, state_dst.name))
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
                                    action = {"index": rule["index"], "action": rule["action"], "reverse": True}

                                # if condition of rule now holds
                                if condition.items() <= state_dst.state.items():
                                    action = {"index": rule["index"], "action": rule["action"], "reverse": False}

                                if action:
                                    self.transitions_change[(state_src.name, state_dst.name)][
                                        "actions"].append(action)

    def del_rules(self, rules):
        # delete actions of rules with index in rule_index in all transitions
        if len(rules) > 0:
            for state_src in self.states:
                for state_dst in self.states:
                    state_src: DeviceState = state_src
                    state_dst: DeviceState = state_dst

                    if state_src != state_dst and state_src.is_consistent and state_dst.is_consistent:
                        changed_element = self.transitions_change.get((state_src.name, state_dst.name))
                        if changed_element:  # if transition between both states
                            for action in changed_element["actions"]:
                                for rule_to_delete in rules:
                                    if action["index"] == rule_to_delete:
                                        changed_element["actions"].remove(action)
                                        break


class SelfLoopException(Exception):
    pass
