import typer
import Pyro4
from typing import List

from constant import *

app = typer.Typer()
daemon = Pyro4.Proxy("PYRONAME:handlers")


@app.command()
def member(name: str, str_ip: str = "*", str_port: str = "*", type: M_TYPE = M_TYPE.PUB.value, action: ACTION = ACTION.ADD.value):

    if(action.value == ACTION.ADD.value):
        print(daemon.add_member(name, str_ip, str_port, type))
    elif(action.value == ACTION.REMOVE.value):
        print(daemon.remove_member(name, type))


@app.command()
def relation(context: List[str], pub: str, sub: str, broker: str = "/", index: int = 0, policy: POLICY = POLICY.ALLOW.value, action: ACTION = ACTION.ADD.value):

    if(action.value == ACTION.ADD.value):
        print(daemon.add_relation(pub, sub, broker, policy.value, context))
    elif(action.value == ACTION.REMOVE.value):
        print(daemon.remove_relation(index))


@app.command()
def rule(src: str = "*", sport: str = "*", dst: str = "*", dport: str = "*", index: int = 0, policy: POLICY = POLICY.ALLOW.value, action: ACTION = ACTION.ADD.value):

    if(action.value == ACTION.ADD.value):
        print(daemon.add_rule(src, sport, dst, dport, policy.value))
    elif(action.value == ACTION.REMOVE.value):
        print(daemon.remove_rule(index))


@app.command()
def show(table: T_TYPE = T_TYPE.RELATIONS.value):
    if(table.value == T_TYPE.RULES.value):
        print(daemon.show_rules())
    elif(table.value == T_TYPE.RELATIONS.value):
        print(daemon.show_relations())


if __name__ == "__main__":
    app()
