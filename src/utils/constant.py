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


class Policy(Enum):
    DROP = "drop"
    ACCEPT = "accept"
    DEFAULT = "default"


class ConstraintType(Enum):
    INT = "int"
    STR = "str"


class FieldType(Enum):
    INT = "int"
    STR = "str"


class TriggerType(Enum):
    TIME = "time"
