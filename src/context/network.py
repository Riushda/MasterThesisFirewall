import itertools as it
import math
import time

from transitions import State
from transitions.extensions import GraphMachine

from context.input import ContextInput
from context.utils import get_device, get_transition_trigger


class SelfLoopException(Exception):
    pass


class DeviceState(State):
    def __init__(self, name, state, is_consistent):
        super().__init__(name, on_enter="enter", on_exit="exit")
        self.state = state
        self.is_consistent = is_consistent
        self.count = 0

    def get_count(self):
        return self.count

    def __repr__(self):
        return str(self.state)

    def enter(self, event):
        self.count += 1
        if not self.is_consistent:
            print("Network log: Entering inconsistent state")

    def exit(self, event):
        if not self.is_consistent:
            print("Network log: Leaving inconsistent state")


class NetworkContext(GraphMachine):
    def __init__(self, context_input: ContextInput):
        self.members = context_input.members
        self.relations = context_input.relations
        self.inconsistent_states = context_input.inconsistent_states
        self.state_inference = context_input.state_inference
        self.relation_mapping = context_input.relation_mapping

        self.device_states = []
        self.transitions = []
        self.transitions_data = {}

        # keep track of current sequence probabilities
        self.proba_queue = []
        self.sequence_proba = 0
        # minimum probability for a transition sequence to be considered as normal, frequent
        self.proba_threshold = 0.05
        # length of the sequence to maintain
        self.k = 10

        # minimum count for a state to become frequent
        self.frequent_state_threshold = 50

        start = time.time_ns()
        initial_state_id = self.build_fsm(context_input.initial_state, context_input.state_combinations)
        end = time.time_ns()
        time_spent = float(end-start)/1000000
        print("time spent building = "+str(time_spent)+" ms")
        print(len(self.transitions))

        super().__init__(states=self.device_states, transitions=self.transitions,
                         initial=initial_state_id,
                         send_event=True)

    def build_fsm(self, initial_state, state_combinations):
        initial_state_id = ""
        # it.product is lazy, one combination is in memory at a given time

        states_ids = {}
        i = 0
        for state in it.product(*(state_combinations[Name] for Name in state_combinations)):
            state = dict(zip(state_combinations.keys(), state))

            states_ids[str(state)] = str(i)

            if state == initial_state:
                initial_state_id = str(i)

            is_src_consistent = self.is_consistent(state)
            self.device_states.append(DeviceState(str(i), state, is_src_consistent))
            i += 1

        for device_state in self.device_states:
            state_src = device_state.state
            state_src_id = states_ids[str(state_src)]

            for field in state_combinations:
                for value in state_combinations[field]:
                    if state_src[field] != value:

                        state_dst = state_src.copy()
                        state_dst[field] = value

                        change = {field: [state_src[field], value]}

                        inferences = self.state_inference.get((field, value))
                        if inferences:
                            for infer in inferences:
                                state_dst[infer[0]] = infer[1]
                                change[infer[0]] = [state_src[infer[0]], infer[1]]

                        state_dst_id = states_ids[str(state_dst)]

                        self.transitions_data[(state_src_id, state_dst_id)] = {"change": change, "actions": [], "count": 0}

                        trigger = get_transition_trigger(field, value)
                        transition = {'trigger': trigger, 'source': state_src_id, 'dest': state_dst_id, 'before': 'update_sequence',
                                      'after': 'action'}
                        self.transitions.append(transition)

        return initial_state_id

    def draw_fsm(self):
        self.get_graph(title=str(self.current_state()), show_roi=True).draw('my_state_diagram.png', prog='dot')

    def is_consistent(self, state):
        for inconsistent in self.inconsistent_states:  # no forbidden state
            if inconsistent.items() <= state.items():
                return False

        return True

    def show_current_state(self):
        print(self.current_state())

    def current_state(self):
        return self.get_state(self.state).state

    def is_current_state_consistent(self):
        return self.get_state(self.state).is_consistent

    def update_sequence(self, event):
        # recalculate the current proba

        transition_count = self.transitions_data[(event.transition.source, event.transition.dest)]["count"]
        state_count = self.get_state(self.state).count

        if state_count >= self.frequent_state_threshold:

            if len(self.proba_queue) == self.k:
                self.sequence_proba -= math.log2(self.proba_queue.pop(0))

            transition_proba = transition_count / state_count
            self.proba_queue.append(transition_proba)
            self.sequence_proba += math.log2(transition_proba)

        if self.sequence_proba < self.proba_threshold and len(self.proba_queue) == self.k:
            # raise alarm
            print("Network log: Infrequent sequence of transition, raising alarm")

        # increase transition counter
        self.transitions_data[(event.transition.source, event.transition.dest)]["count"] += 1

    def run_action(self, trigger):
        reverse = trigger["reverse"]
        action = next(iter(trigger["action"]))
        relation = trigger["action"][action]
        mark = self.relations[relation].mark
        subject = self.relations[relation].subject

        if (action == "enable" and not reverse) or (action == "disable" and reverse):
            self.relation_mapping.enable_relation(mark, subject)
        elif (action == "disable" and not reverse) or (action == "enable" and reverse):
            self.relation_mapping.disable_relation(mark, subject)

    def action(self, event):
        # perform actions of transition
        actions = self.transitions_data[(event.transition.source, event.transition.dest)]["actions"]
        # print("list_actions : " + str(actions))
        for action in actions:
            # print("action : " + str(action))
            self.run_action(action)

    def self_loop(self, data):
        state = self.current_state()
        return state[data[0]] == data[1]

    # add actions of triggers in all transitions validating the conditions
    def add_triggers(self, triggers):
        for state_src in self.device_states:
            for state_dst in self.device_states:
                state_src: DeviceState = state_src
                state_dst: DeviceState = state_dst

                if state_src.name != state_dst.name and state_src.is_consistent and state_dst.is_consistent:

                    changed_element = self.transitions_data.get((state_src.name, state_dst.name))
                    if changed_element:  # if transition between both states
                        changed_element = changed_element["change"]
                        changed_element_keys = list(changed_element.keys())

                        for trigger in triggers:
                            condition = trigger["condition"]

                            condition_changed = False
                            for key in changed_element_keys:
                                if key in condition:
                                    condition_changed = True
                                    break

                            if condition_changed:
                                action = None

                                # if condition of trigger does no longer hold
                                if condition.items() <= state_src.state.items():
                                    action = {"index": trigger["index"], "action": trigger["action"], "reverse": True}

                                # if condition of trigger now holds
                                if condition.items() <= state_dst.state.items():
                                    action = {"index": trigger["index"], "action": trigger["action"], "reverse": False}

                                if action:
                                    self.transitions_data[(state_src.name, state_dst.name)][
                                        "actions"].append(action)

    # delete actions of triggers with index in trigger_index in all transitions
    def del_triggers(self, triggers):
        if len(triggers) > 0:
            for state_src in self.device_states:
                for state_dst in self.device_states:
                    state_src: DeviceState = state_src
                    state_dst: DeviceState = state_dst

                    if state_src != state_dst and state_src.is_consistent and state_dst.is_consistent:
                        changed_element = self.transitions_data.get((state_src.name, state_dst.name))
                        if changed_element:  # if transition between both states
                            for action in changed_element["actions"]:
                                for trigger_to_delete in triggers:
                                    if action["index"] == trigger_to_delete:
                                        changed_element["actions"].remove(action)
                                        break
