from enum import Enum


class PolicyJson(Enum):
    DROP = {"drop": ""}
    ACCEPT = {"accept": ""}
    DEFAULT = {"drop": ""}


class Policy(Enum):
    DROP = "drop"
    ACCEPT = "accept"
