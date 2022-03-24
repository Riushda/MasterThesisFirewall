from multiprocessing import Queue
import Pyro4
import time
from network_context import NetworkContext
from network_context import SelfLoopException
from abstract_rule import AbstractRule
from context_utils import *

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


def test():
    global network_state
    global abstract_rules
    init()

    categorizer = Categorizer()

    temp_intervals = [-np.inf, 0, 25, np.inf]
    temp_labels = ['cold', 'average', 'hot']
    categorizer.add_mapping("thermo.temp", temp_intervals, temp_labels)

    # To input like this
    initial_state_json = {"mvt_sensor": {"lastMessage": "long"}, "lamp": {"status": "off"},
                          "thermo": {"temp": "cold", "lastMessage": "recent"}, "heater": {"status": "on"},
                          "window": {"status": "closed"}}  # check how to enable/disable  rules from initial state

    # but will be converted to this
    initial_state = flatten_state(initial_state_json)

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

    # contains actions to take if condition is met
    abstract_rules = [{"condition": {"mvt_sensor.lastMessage": "long", "window.status": "closed"},
                       "action": {"disable": {"src": "window_switch", "dst": "window"}}}
                      ]

    pub_list = {"thermo": 0, "mvt_sensor": 0}
    relations = {}

    # last message triggers a timer in the machine fms after the .trigger call ?
    network_context = NetworkContext(pub_list, relations, initial_state, state_combinations, inconsistent_states,
                                     state_inference)
    rules = AbstractRule(abstract_rules, network_context)

    rule = {"condition": {"thermo.temp": "hot", "heater.status": "off"},
            "action": {"disable": {"src": "heater_switch", "dst": "heater"}}}

    rule_index = rules.add_rule(rule)
    rule_index = rules.del_rule(rule_index)
    rule_index = rules.add_rule(rule)

    network_context.show_current_state()

    update_context(network_context, categorizer, ("thermo.temp", -1))  # self loop
    update_context(network_context, categorizer, ("thermo.temp", 26))
    network_context.show_current_state()
    update_context(network_context, categorizer, ("thermo.temp", -2))
    network_context.show_current_state()
    update_context(network_context, categorizer, ("heater.status", "on"))
    network_context.show_current_state()
    update_context(network_context, categorizer, ("window.status", "open"))
    network_context.show_current_state()
    update_context(network_context, categorizer, ("window.status", "closed"))
    network_context.show_current_state()

    ''' For efficiency test later
    start = time.time()
    end = time.time()
    print(end - start)
    '''


def update_context(network_context: NetworkContext, categorizer: Categorizer, packet_data):

    if categorizer.has_mapping(packet_data[0]):
        label = categorizer.map(packet_data[0], packet_data[1])
        packet_data = (packet_data[0], label)

    try:
        network_context.evaluate(data=packet_data)
    except SelfLoopException:
        print("self loop")
        return False

    return True


test()

