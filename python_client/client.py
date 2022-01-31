import typer
import Pyro4

from constant import *
import member as members

app = typer.Typer()
daemon = Pyro4.Proxy("PYRONAME:handlers")


@app.command()
def member(name: str, str_ip: str = "*", str_port: str = "*", type: M_TYPE = M_TYPE.PUB.value, action: ACTION = ACTION.ADD.value):

    member = members.parse_member(name, str_ip, str_port, type)

    if(not member):
        return

    if(action.value == ACTION.ADD.value):
        print(daemon.add_member(member.name, member.ip,
              member.bitmask, member.port, member.n_port, member.type))
    elif(action.value == ACTION.REMOVE.value):
        print(daemon.remove_member(name, type))


@app.command()
def relation(pub: str = "dev", sub: str = "dev", broker: str = "/", context: str = "/", index: int = 0, policy: str = "allow", action: ACTION = ACTION.ADD.value):

    int_policy = 1
    if(policy == "deny"):
        int_policy = 0

    if(action.value == ACTION.ADD.value):
        print(daemon.add_relation(pub, sub, broker, int_policy, context))
    elif(action.value == ACTION.REMOVE.value):
        print(daemon.remove_relation(index))


@app.command()
def rule(src: str = "*", sport: str = "*", dst: str = "*", dport: str = "*", index: int = 0, policy: str = "allow", action: ACTION = ACTION.ADD.value):

    int_policy = 1
    if(policy == "deny"):
        int_policy = 0

    src_member = members.parse_member("", src, sport, "")
    if(not src_member):
        return

    dst_member = members.parse_member("", dst, dport, "")
    if(not dst_member):
        return

    if(action.value == ACTION.ADD.value):
        print(daemon.add_rule(src_member.ip, src_member.bitmask, src_member.port, src_member.n_port,
                              dst_member.ip, dst_member.bitmask, dst_member.port, dst_member.n_port, int_policy))
    elif(action.value == ACTION.REMOVE.value):
        print(daemon.remove_rule(index))


@ app.command()
def show(table: T_TYPE = T_TYPE.RELATIONS.value):
    if(table.value == T_TYPE.RULES.value):
        print(daemon.show_rules())
    elif(table.value == T_TYPE.RELATIONS.value):
        print(daemon.show_relations())


# @app.command()
# def traceback():
#     try:
#         result = daemon.print_relations()
#     except Exception:
#         print("Pyro traceback:")
#         print("".join(Pyro4.util.getPyroTraceback()))
if __name__ == "__main__":
    app()
