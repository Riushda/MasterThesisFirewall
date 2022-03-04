NFTABLES_INIT = {"nftables": [
    {"flush": {"ruleset": None}},
    {"add": {"table": {
        "family": "ip",
        "name": "filter"
    }}},
    {"add": {"chain": {
        "family": "ip",
        "table": "filter",
        "name": "INPUT"
    }}},
    {"add": {"chain": {
        "family": "ip",
        "table": "filter",
        "name": "OUTPUT"
    }}},
    {"add": {"chain": {
        "family": "ip",
        "table": "filter",
        "name": "FORWARD"
    }}}
]}

NFTABLES_ADD_RULE = {"nftables": [
    {"add": {"rule": {
        "family": "ip",
        "table": "filter",
        "chain": "INPUT",
        "expr": [
            {
                "accept": None
            }
        ]
    }}}
]}

NFTABLES_MARK = {"mangle": {"key": 
                        {"meta": {"key": "mark"}}, 
                        "value": 0}}

NFTABLES_PORT_MATCHING = [{
                "match":{
                    "op":"==",
                    "left":{
                    "meta":{
                        "key":"l4proto"
                    }
                    },
                    "right":{
                    "set":[
                        "tcp",
                        "udp"
                    ]
                    }
                }
            },
            {
                "match":{
                    "op":"==",
                    "left":{
                    "payload":{
                        "protocol":"th",
                        "field":"dport"
                    }
                    },
                    "right": 0 # specified port
                }
            }]

NFTABLES_LIST_CHAIN = {"nftables": [
    {"list": {"chain": {
        "family": "ip",
        "table": "filter",
        "name": "INPUT"
    }}}
]}