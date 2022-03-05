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
        "expr": [{
                "match":{
                    "op":"==",
                    "left": {"meta": {
                        "key":"l4proto"}},
                    "right": {"set": ["tcp","udp"]}}
                },
                {
                    "accept": None
                }
            ]
    }}}
]}

NFTABLES_MARK = {"mangle": {"key": 
                        {"meta": {"key": "mark"}}, 
                        "value": 0}}

NFTABLES_IP_MATCHING = {"match": 
                            {"op": "==", 
                            "left": {"payload": 
                                        {"protocol": "ip", "field": ""}}, # field is either saddr or daddr 
                            "right": {"prefix":  
                                        {"addr": "", "len": 0}} # set ip as string and the mask as int
                            }
                        }

NFTABLES_PORT_MATCHING = {
                            "match":{
                                "op":"==",
                                "left":{
                                "payload":{
                                    "protocol":"th",
                                    "field":"" # specify sport or dport
                                }
                                },
                                "right": 0 # specified port
                            }
                         }

NFTABLES_LIST_CHAIN = {"nftables": [
                        {"list": {"chain": {
                            "family": "ip",
                            "table": "filter",
                            "name": "INPUT"
                        }}}
                    ]}