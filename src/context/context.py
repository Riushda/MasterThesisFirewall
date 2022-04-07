from multiprocessing import Queue
from _queue import Empty

from transitions import MachineError

from context.abstract_rule import AbstractRule
from context.network_context import NetworkContext
from context.network_context import SelfLoopException
from nfqueue.abstract_packet import AbstractPacket
from context.utils import InputParser, Categorizer, is_float


def run(packet_queue: Queue, pub_list, sub_list, broker_list, relations):
    input_parser: InputParser = InputParser()
    categorizer: Categorizer = Categorizer()

    initial_state, state_combinations, inconsistent_states, state_inference, abstract_rules, categorization = input_parser.get_input()

    categorizer.add_mapping_array(categorization)

    network_context = NetworkContext(pub_list, relations, initial_state, state_combinations, inconsistent_states,
                                     state_inference)

    rules = AbstractRule(abstract_rules, network_context)  # pass this to the client later

    network_context.draw_fsm()

    while True:
        try:
            packet: AbstractPacket = packet_queue.get(block=True, timeout=10)

            for content in packet.content:
                device = get_device_name(packet.src, pub_list)
                update_context(network_context, device, categorizer, content)
                network_context.show_current_state()
                network_context.draw_fsm()

        except Empty:
            pass


def update_context(network_context: NetworkContext, device, categorizer: Categorizer, packet_data):
    try:

        field = device + "." + packet_data[0]

        value = packet_data[1]
        if is_float(value):
            value = float(value)

        if categorizer.has_mapping(field):
            value = categorizer.map(field, value)

        print(field, value)
        trigger = network_context.get_transition_trigger(field, value)

        try:
            network_context.trigger(trigger, data=(field, value))
        except MachineError as e:
            if network_context.self_loop((field, value)):
                raise SelfLoopException()
            else:
                print("MachineError: " + str(e))
                return False

        except AttributeError as e:
            print(str(e))
            return False

    except SelfLoopException:
        print("Self Loop")
        return False

    return True


def get_device_name(ip, pub_list):
    for pub in pub_list:
        if pub_list[pub].ip == ip:
            return pub_list[pub].name

    return None


def test():
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
    network_context = NetworkContext(pub_list, relations, initial_state, state_combinations, inconsistent_states,
                                     state_inference)
    rules = AbstractRule(abstract_rules, network_context)

    rule = {"condition": {"thermo.temp": "hot", "heater.status": "off"},
            "action": {"disable": {"src": "heater_switch", "dst": "heater"}}}

    rule_index = rules.add_rule(rule)
    rule_index = rules.del_rule(rule_index)
    rule_index = rules.add_rule(rule)

    network_context.show_current_state()

    update_context(network_context, ("thermo.temp", "cold"))  # self loop
    update_context(network_context, ("thermo.temp", "hot"))
    network_context.show_current_state()
    update_context(network_context, ("thermo.temp", "cold"))
    network_context.show_current_state()
    update_context(network_context, ("heater.status", "on"))
    network_context.show_current_state()
    update_context(network_context, ("window.status", "open"))
    network_context.show_current_state()
    update_context(network_context, ("window.status", "closed"))
    network_context.show_current_state()

    ''' For efficiency test later
    start = time.time()
    end = time.time()
    print(end - start)
    '''

# test()
