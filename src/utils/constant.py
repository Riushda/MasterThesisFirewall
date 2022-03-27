from enum import Enum


class Action(Enum):
    ADD = "add"
    REMOVE = "rm"


class Command(Enum):
    MEMBER = "member"
    RELATION = "relation"
    RULE = "rule"
    SHOW = "show"


class Code(Enum):
    PID = 0
    ADD_RELATION = 1
    RM_RELATION = 2
    ENABLE_RELATION = 3
    DISABLE_RELATION = 4


class StringConstraintType(Enum):
    SUBJECT = "subject"
    INT = "int"
    STR = "str"
    TIME = "time"


class ConstraintType(Enum):
    SUBJECT = 0
    INT = 1
    STR = 2
    TIME = 3


class MemberType(Enum):
    DEVICE = "device"
    BROKER = "broker"
    PUB = "pub"
    SUB = "sub"


class TableType(Enum):
    RULES = "rules"
    RELATIONS = "relations"


class Policy(Enum):
    DROP = "drop"
    ACCEPT = "accept"
    DEFAULT = "default"
