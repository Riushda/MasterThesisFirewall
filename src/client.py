import argparse

import Pyro4

from utils.constant import *

daemon = Pyro4.Proxy("PYRONAME:ClientHandlers")
parser = argparse.ArgumentParser()

parser.add_argument("command", type=str, choices=[
    "member", "relation", "rule", "show"])

parser.add_argument("--action", type=str,
                    choices=[e.value for e in Action], default=Action.ADD.value)

# Parameters related to members

parser.add_argument("--name", type=str,
                    help="name of the member", default=None)

parser.add_argument("--src", type=str,
                    help="ip with optional bitmask and port", default=None)

parser.add_argument("--ip", type=str,
                    help="ip with optional bitmask", default=None)

parser.add_argument("--port", type=str,
                    help="port", default=None)

parser.add_argument("--type", type=str, choices=[e.value for e in MemberType],
                    help="type of device", default=MemberType.PUB.value)

# Parameters related to relations

parser.add_argument("--policy", type=str, choices=[e.value for e in Policy],
                    help="policy to adopt", default=Policy.ACCEPT.value)

parser.add_argument("--index", type=int,
                    help="index to remove", default=0)

parser.add_argument("--pub", type=str,
                    help="a publisher", default=None)

parser.add_argument("--sub", type=str,
                    help="a subscriber", default=None)

parser.add_argument("--broker", type=str,
                    help="a broker", default=None)

parser.add_argument("--constraint", action='append',
                    help='a constraint on the context', default=[])

# Parameters related to show

parser.add_argument("--table", type=str, choices=[e.value for e in TableType],
                    help="table to display", default="relations")

args = parser.parse_args()

match args.command:
    case Command.MEMBER.value:
        match args.action:
            case Action.ADD.value:
                print(daemon.add_member(args.name, args.src, args.type))
            case Action.REMOVE.value:
                print(daemon.remove_member(args.name, args.type))
    case Command.RELATION.value:
        match args.action:
            case Action.ADD.value:
                print(daemon.add_relation(args.pub, args.sub,
                                          args.broker, args.policy, args.constraint))
            case Action.REMOVE.value:
                print(daemon.remove_relation(args.index))
    case Command.SHOW.value:
        print(daemon.show(args.table))
