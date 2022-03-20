from multiprocessing import Queue
from transitions import Machine, State, EventData
import Pyro4
import itertools as it
import time

from daemon.member import Member

daemon = Pyro4.Proxy("PYRONAME:handlers")
'''
daemon functions that will be called 

daemon.add_member(name, str_ip, str_port, type)
daemon.remove_member(name, type)
daemon.add_relation(pub, sub, broker, policy, context)
daemon.remove_relation(index)
daemon.add_rule(src, sport, dst, dport, policy)
daemon.remove_rule(index)
'''


def init():
    global network_state
    global abstract_rules
    network_state = {}
    abstract_rules = []


def run(packet_queue: Queue, pub_list, sub_list, broker_list, relations):
    init()

    while True:
        try:
            packet = packet_queue.get(block=True, timeout=10)
            print(packet)
        except:
            print("No packet within timeout seconds")


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
    def __init__(self, initial_state, state_combinations, abstract_rules, inconsistent_states, state_inference):

        self.abstract_rules = abstract_rules
        self.states = []
        self.transitions = []
        self.transitions_change = dict()
        self.inconsistent_states = inconsistent_states
        self.state_inference = state_inference

        initial_state_name = ""
        i = 0
        # it.product is lazy, one combination is in memory at a given time
        for state_src in it.product(*(state_combinations[Name] for Name in state_combinations)):
            state_src = dict(zip(state_combinations.keys(), state_src))
            if state_src == initial_state:
                initial_state_name = str(i)
            # print(state_src)

            is_src_consistent = self.is_consistent(state_src)
            self.states.append(DeviceState(str(i), state_src, is_src_consistent))

            j = 0
            for state_dst in it.product(*(state_combinations[Name] for Name in state_combinations)):
                state_dst = dict(zip(state_combinations.keys(), state_dst))
                # print(state_dst)

                is_dst_consistent = self.is_consistent(state_dst)

                # get all keys in state_src and state dst which doesn't have the same value
                diff_keys = [key for key in state_src.keys() & state_dst if state_src[key] != state_dst[key]]

                conforming = False

                # no state self loop and transition only between states with 1 difference
                if len(diff_keys) == 1:
                    infer = self.state_inference.get((diff_keys[0], state_dst[diff_keys[0]]))
                    if infer is None or state_dst[infer[0][0]] == infer[0][1]:
                        conforming = True
                        # print(str(state_src[key[0]]) + " != " + str(state_dst[key[0]]))
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
                                    self.transitions_change[(str(i), str(j))]["change"][element] = [state_src[element], state_dst[element]]
                                break

                if conforming:
                    transition = {'trigger': 'evaluate', 'source': str(i), 'dest': str(j),
                                  'conditions': 'check_transition', 'after': 'action'}

                    self.transitions.append(transition)
                    if is_src_consistent and is_dst_consistent:
                        self.set_transition_action(transition, state_src, state_dst)

                j += 1

            i += 1

        self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial=initial_state_name,
                               send_event=True)

    def is_consistent(self, state):
        for inconsistent in self.inconsistent_states:  # no forbidden state
            if inconsistent.items() <= state.items():
                return False

        return True

    def set_transition_action(self, transition, state_src, state_dst):
        changed_element = self.transitions_change[(transition["source"], transition["dest"])]["change"]
        changed_element_keys = list(changed_element.keys())

        for rule in self.abstract_rules:
            condition = rule["condition"]

            condition_changed = False
            for key in changed_element_keys:
                if key in condition:
                    condition_changed = True
                    break

            if condition_changed:
                action = None

                # if condition of rule does no longer hold
                if condition.items() <= state_src.items():
                    action = {"index": rule["index"], "reverse action": rule["action"]}

                # if condition of rule now holds
                if condition.items() <= state_dst.items():
                    action = {"index": rule["index"], "action": rule["action"]}

                if action:
                    self.transitions_change[(transition["source"], transition["dest"])]["actions"].append(action)

    def add_rule(self, rule):
        index = 0
        for abs_rule in self.abstract_rules:
            if index < abs_rule["index"]:
                break
            else:
                index += 1

        rule["index"] = index
        self.abstract_rules.append(rule)

        for state_src in self.states:
            for state_dst in self.states:
                if state_src.name != state_dst.name:

                    changed_element = self.transitions_change.get((state_src.name, state_dst.name))

                    if changed_element:  # if transition between both states
                        changed_element = changed_element["change"]
                        changed_element_keys = list(changed_element.keys())

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
                                self.transitions_change[(state_src.name, state_dst.name)]["actions"].append(action)

        return rule["index"]

    def del_rule(self, rule_index):
        deleted = False
        for i in range(len(self.abstract_rules)):
            if self.abstract_rules[i]["index"] == rule_index:
                del self.abstract_rules[i]
                deleted = True
                break

        if deleted:
            for state_src in self.states:
                for state_dst in self.states:
                    if state_src != state_dst:
                        changed_element = self.transitions_change.get((state_src.name, state_dst.name))
                        if changed_element:  # if transition between both states
                            for action in changed_element["actions"]:
                                if action["index"] == rule_index:
                                    changed_element["actions"].remove(action)
                                    break
            return rule_index
        else:
            return -1

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


def test():
    global network_state
    global abstract_rules
    init()

    # To input like this
    initial_state_json = {"mvt_sensor": {"lastMessage": "long"}, "lamp": {"status": "off"},
                          "thermo": {"temp": "hot", "lastMessage": "recent"}, "heater": {"status": "off"},
                          "window": {"status": "open"}}  # check how to enable/disable  rules from initial state

    # but will be converted to this
    initial_state = {"mvt_sensor.lastMessage": "long", "lamp.status": "off",
                     "thermo.temp": "cold", "thermo.lastMessage": "recent", "heater.status": "on",
                     "window.status": "closed"}  # check how to enable/disable  rules from initial state

    # contains all possible values for all devices fields
    state_combinations = {"thermo.temp": ["cold", "average", "hot"], "mvt_sensor.lastMessage": ["recent", "long"],
                          "thermo.lastMessage": ["recent", "long"], "window.status": ["open", "closed"],
                          "heater.status": ["on", "off"], "lamp.status": ["on", "off"]}

    # explicitly forbid state
    inconsistent_states = [{"heater.status": "on", "window.status": "open"},
                           {"thermo.temp": "hot", "heater.status": "on"}]

    # infer state of one or multiple devices when a message from another device is received
    state_inference = {("thermo.temp", "hot"): [("heater.status", "off")],
                       # for example add ("air_conditioner.status": "on")
                       ("mvt_sensor.lastMessage", "recent"): [("lamp.status", "on")]}

    pub_list = {}
    relations = {}
    check = True
    #check = check_inferences(state_inference, pub_list, relations)
    if not check:
        return

    # contains actions to take if condition is met
    abstract_rules = [{"index": 0, "condition": {"mvt_sensor.lastMessage": "long", "window.status": "closed"},
                       "action": {"disable": {"src": "window_switch", "dst": "window"}}}
                      ]

    # last message triggers a timer in the machine fms after the .trigger call ?
    network_context = NetworkContext(initial_state, state_combinations, abstract_rules, inconsistent_states,
                                     state_inference)

    rule = {"condition": {"thermo.temp": "hot", "heater.status": "off"},
            "action": {"disable": {"src": "heater_switch", "dst": "heater"}}}

    rule_index = network_context.add_rule(rule)
    # rule_index = network_context.del_rule(rule_index)
    # rule_index = network_context.add_rule(rule)

    network_context.show_current_state()
    network_context.evaluate(data=("thermo.temp", "hot"))
    network_context.show_current_state()
    network_context.evaluate(data=("thermo.temp", "cold"))
    network_context.show_current_state()
    network_context.evaluate(data=("heater.status", "on"))
    network_context.show_current_state()
    network_context.evaluate(data=("window.status", "open"))
    network_context.show_current_state()
    network_context.evaluate(data=("window.status", "closed"))
    network_context.show_current_state()

    ''' For efficiency test later
    start = time.time()
    end = time.time()
    print(end - start)
    '''


# check that the inferences keys are publishers and that the values are the subscribers of their key
def check_inferences(state_inference, pub_list, relations):
    keys = state_inference.keys()

    for key in keys:
        device = get_device(key[0])

        # check if keys are publishers
        if device not in pub_list:
            print(device + " : keys in inferences must be publishers !")
            return False

        # check if values are subscribers of their key

        values = state_inference[key]
        devices = []
        for value in values:
            devices.append(get_device(value))

        for relation in relations:
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
            print(str(devices) + " : values in inferences must be subscribers of their key !")
            return False

    return True


def get_device(field):
    key_list = field.split(".")
    return key_list[0]


def is_member(field, member_list):
    key_list = field.split(".")
    return key_list[0] in member_list


def get_element(json, field):
    element = None
    key_list = field.split(".")
    for key in key_list:
        if element:
            element = element[key]
        else:
            element = json[key]

    return element


test()
