import itertools as it

from transitions import Machine, State


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

                # get all keys in state_src and state dst which doesn't have the same value
                diff_keys = [key for key in state_src.keys() & state_dst if state_src[key] != state_dst[key]]

                conforming = False

                # no state self loop and transition only between states with 1 difference
                if len(diff_keys) == 1:
                    infer = self.state_inference.get((diff_keys[0], state_dst[diff_keys[0]]))
                    if infer is None or state_dst[infer[0][0]] == infer[0][1]:
                        conforming = True
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
                                self.transitions_change[(str(i), str(j))] = {"change": {}, "actions": []}
                                for element in diff_keys:
                                    self.transitions_change[(str(i), str(j))]["change"][element] = [state_src[element],
                                                                                                    state_dst[element]]
                                break

                if conforming:
                    transition = {'trigger': 'evaluate', 'source': str(i), 'dest': str(j),
                                  'conditions': 'check_transition', 'after': 'action'}

                    self.transitions.append(transition)

                j += 1

            i += 1

        self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial=initial_state_name,
                               prepare_event='forbid_self_loop', send_event=True)

    def is_consistent(self, state):
        for inconsistent in self.inconsistent_states:  # no forbidden state
            if inconsistent.items() <= state.items():
                return False

        return True

    def show_current_state(self):
        print(self.machine.get_state(self.state).state)

    def is_current_state_consistent(self):
        return self.machine.get_state(self.state).is_consistent

    def action(self, event):
        # print("action: " + str(event))
        actions = self.transitions_change[(event.transition.source, event.transition.dest)]["actions"]
        print(actions)

    def check_transition(self, event):
        # print("condition: " + str(event.kwargs["data"]))
        data = event.kwargs["data"]

        elements = self.transitions_change[(event.transition.source, event.transition.dest)]["change"]

        for key in elements:
            if key == data[0] and elements[key][1] == data[1]:
                return True

        return False

    def forbid_self_loop(self, event):
        data = event.kwargs["data"]
        state = self.machine.get_state(self.state).state
        if state[data[0]] == data[1]:
            raise SelfLoopException()

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


class SelfLoopException(Exception):
    pass
