from multiprocessing import Queue
import Pyro4
import time
from network_context import NetworkContext
from abstract_rule import AbstractRule

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

    # contains actions to take if condition is met
    abstract_rules = [{"condition": {"mvt_sensor.lastMessage": "long", "window.status": "closed"},
                       "action": {"disable": {"src": "window_switch", "dst": "window"}}}
                      ]

    pub_list = {"thermo": 0, "mvt_sensor": 0}
    relations = {}

    # last message triggers a timer in the machine fms after the .trigger call ?
    network_context = NetworkContext(pub_list, relations, initial_state, state_combinations, inconsistent_states, state_inference)
    rules = AbstractRule(abstract_rules, network_context)

    rule = {"condition": {"thermo.temp": "hot", "heater.status": "off"},
            "action": {"disable": {"src": "heater_switch", "dst": "heater"}}}

    rule_index = rules.add_rule(rule)
    rule_index = rules.del_rule(rule_index)
    rule_index = rules.add_rule(rule)

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


test()
