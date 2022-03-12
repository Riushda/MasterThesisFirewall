from multiprocessing import Queue
from transitions import Machine, State, EventData
import Pyro4
import itertools as it

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
    def __init__(self, name, state):
        super().__init__(name)
        self.state = state


class NetworkContext(object):
    def __init__(self, initial_state, state_combinations, abstract_rules, forbidden_states, state_inference):

        self.abstract_rules = abstract_rules
        self.states = []
        self.transitions = []
        self.transitions_change = {}
        self.forbidden_states = forbidden_states
        self.state_inference = state_inference

        initial_state_name = ""
        i = 0
        # it.product is lazy, one combination is in memory at a given time
        for state_src in it.product(*(state_combinations[Name] for Name in state_combinations)):
            state_src = dict(zip(state_combinations.keys(), state_src))
            if state_src == initial_state:
                initial_state_name = str(i)
            # print(state_src)

            if self.is_allowed(state_src):
                self.states.append(DeviceState(str(i), state_src))

                j = 0
                for state_dst in it.product(*(state_combinations[Name] for Name in state_combinations)):
                    state_dst = dict(zip(state_combinations.keys(), state_dst))
                    # print(state_dst)

                    if self.is_allowed(state_dst):

                        # get all keys in state_src and state dst which doesn't have the same value
                        diff_keys = [key for key in state_src.keys() & state_dst if state_src[key] != state_dst[key]]

                        conforming = False

                        # no state self loop and transition only between states with 1 difference
                        if len(diff_keys) == 1:
                            infer = self.state_inference.get((diff_keys[0], state_dst[diff_keys[0]]))
                            if infer is None or state_dst[infer[0]] == infer[1]:
                                conforming = True
                                # print(str(state_src[key[0]]) + " != " + str(state_dst[key[0]]))
                                self.transitions_change[(str(i), str(j))] = {
                                    diff_keys[0]: [state_src[diff_keys[0]], state_dst[diff_keys[0]]]}

                        # 2 different keys between state_src and state_dst, changing one key could infer a change
                        # in the second one resulting in state_dst with 2 different fields without intermediate state
                        elif len(diff_keys) == 2:
                            infer1 = self.state_inference.get((diff_keys[0], state_dst[diff_keys[0]]))
                            infer2 = self.state_inference.get((diff_keys[1], state_dst[diff_keys[1]]))

                            condition1 = infer1 and infer1 == (diff_keys[1], state_dst[diff_keys[1]])
                            condition2 = infer2 and infer2 == (diff_keys[0], state_dst[diff_keys[0]])
                            if condition1:
                                conforming = True
                                self.transitions_change[(str(i), str(j))] = {
                                    diff_keys[0]: [state_src[diff_keys[0]], state_dst[diff_keys[0]]],
                                    diff_keys[1]: [state_src[diff_keys[1]], state_dst[diff_keys[1]]]}

                            if condition2:
                                conforming = True
                                self.transitions_change[(str(i), str(j))] = {
                                    diff_keys[1]: [state_src[diff_keys[1]], state_dst[diff_keys[1]]],
                                    diff_keys[0]: [state_src[diff_keys[0]], state_dst[diff_keys[0]]]}

                        if conforming:
                            self.transitions.append(
                                {'trigger': 'evaluate', 'source': str(i), 'dest': str(j),
                                 'conditions': 'check_transition',
                                 'after': 'action'})
                    j += 1

            i += 1

        # print(self.transitions_change)
        # print(self.abstract_rules)

        self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial=initial_state_name,
                               send_event=True)

    def show_current_state(self):
        print(self.machine.get_state(self.state).state)

    def is_allowed(self, state):
        for forbidden in self.forbidden_states:  # no forbidden state
            if forbidden.items() <= state.items():
                return False

        return True

    def action(self, event):
        # print("action: " + str(event))
        data = event.kwargs["data"]

        previous_state: DeviceState = self.machine.get_state(event.transition.source)
        current_state: DeviceState = self.machine.get_state(event.transition.dest)

        changed_element = self.transitions_change[(event.transition.source, event.transition.dest)]
        iterator = iter(changed_element)
        key1 = next(iterator, None)
        key2 = next(iterator, None)  # can be None

        for rule in self.abstract_rules:
            condition = rule["condition"]

            if key1 in condition or key2 in condition:

                # if condition of rule does no longer hold
                if condition.items() <= previous_state.state.items():
                    print("reverse action : " + str(rule["action"]))

                # if condition of rule now holds
                if condition.items() <= current_state.state.items():
                    print("action : " + str(rule["action"]))

    def check_transition(self, event):
        # print("condition: " + str(event.kwargs["data"]))
        data = event.kwargs["data"]

        element = self.transitions_change[(event.transition.source, event.transition.dest)]

        element_key = next(iter(element))

        return element_key == data[0] and data[1] == element[element_key][1]


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
                     "thermo.temp": "hot", "thermo.lastMessage": "recent", "heater.status": "off",
                     "window.status": "open"}  # check how to enable/disable  rules from initial state

    # contains all possible values for all devices fields
    state_combinations = {"thermo.temp": ["cold", "average", "hot"], "mvt_sensor.lastMessage": ["recent", "long"],
                          "thermo.lastMessage": ["recent", "long"], "window.status": ["open", "closed"],
                          "heater.status": ["on", "off"], "lamp.status": ["on", "off"]}

    # explicitly forbid state
    forbidden_states = [{"heater.status": "on", "window.status": "open"}, {"thermo.temp": "hot", "heater.status": "on"}]

    # infer state of one or multiple devices when a message from another device is received
    # TODO : make it possible to infer the state of multiples devices from one message
    #  (array of tuples instead of one tuple in the value), len(diff_keys) will be 2 or greater now
    state_inference = {("thermo.temp", "hot"): ("heater.status", "off"), # for example add ("air_conditioner.status": "on")
                       ("mvt_sensor.lastMessage", "recent"): ("lamp.status", "on")}

    # contains actions to take if condition is met
    abstract_rules = [
        {"condition": {"thermo.temp": "hot", "heater.status": "off"},
         "action": {"disable": {"src": "heater_switch", "dst": "heater"}}},
        {"condition": {"mvt_sensor.lastMessage": "long", "window.status": "closed"},
         "action": {"disable": {"src": "window_switch", "dst": "window"}}}]

    # last message triggers a timer in the machine fms after the .trigger call ?
    network_context = NetworkContext(initial_state, state_combinations, abstract_rules, forbidden_states,
                                     state_inference)
    network_context.show_current_state()
    network_context.evaluate(data=("thermo.temp", "cold"))
    network_context.show_current_state()
    network_context.evaluate(data=("thermo.temp", "hot"))
    network_context.show_current_state()


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
