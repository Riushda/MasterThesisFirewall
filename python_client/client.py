import argparse
import Pyro4

from constant import *

daemon = Pyro4.Proxy("PYRONAME:handlers")
parser = argparse.ArgumentParser()

parser.add_argument("command", type=str, choices=[
                    "member", "relation", "rule", "show"])

parser.add_argument("--action", type=str,
                    choices=[e.value for e in ACTION], default=ACTION.ADD.value)


# Parameters related to members

parser.add_argument("--name", type=str,
                    help="name of the member", default="dev")

parser.add_argument("--ip", type=str,
                    help="ip with optional bitmask", default="*")

parser.add_argument("--port", type=str,
                    help="port", default="*")

parser.add_argument("--type", type=str, choices=[e.value for e in M_TYPE],
                    help="type of device", default=M_TYPE.PUB.value)

# Parameters related to relations and rules

parser.add_argument("--policy", type=str, choices=[e.value for e in POLICY],
                    help="policy to adopt", default=POLICY.ALLOW.value)

parser.add_argument("--index", type=int,
                    help="index to remove", default=0)

# Parameters related to relations

parser.add_argument("--pub", type=str,
                    help="a publisher", default="dev")

parser.add_argument("--sub", type=str,
                    help="a subscriber", default="dev")

parser.add_argument("--broker", type=str,
                    help="a broker", default="dev")

parser.add_argument("--constraint", action='append',
                    help='a constraint on the context', default=[])

# Parameters related to rules

parser.add_argument("--src", type=str,
                    help="ip with optional bitmask", default="*")

parser.add_argument("--dst", type=str,
                    help="ip with optional bitmask", default="*")

parser.add_argument("--sport", type=str,
                    help="source port", default="*")

parser.add_argument("--dport", type=str,
                    help="destination port", default="*")

# Parameters related to show

parser.add_argument("--table", type=str, choices=[e.value for e in T_TYPE],
                    help="table to display", default="relations")

args = parser.parse_args()

match args.command:
    case COMMAND.MEMBER.value:
        match args.action:
            case ACTION.ADD.value:
                print(daemon.add_member(args.name, args.ip, args.port, args.type))
            case ACTION.REMOVE.value:
                print(daemon.remove_member(args.name, args.type))
    case COMMAND.RELATION.value:
        match args.action:
            case ACTION.ADD.value:
                print(daemon.add_relation(args.pub, args.sub,
                      args.broker, args.policy, args.constraint))
            case ACTION.REMOVE.value:
                print(daemon.remove_relation(args.index))
    case COMMAND.RULE.value:
        match args.action:
            case ACTION.ADD.value:
                print(daemon.add_rule(args.src, args.sport,
                      args.dst, args.dport, args.policy))
            case ACTION.REMOVE.value:
                print(daemon.remove_rule(args.index))
    case COMMAND.SHOW.value:
        print(daemon.show(args.table))
