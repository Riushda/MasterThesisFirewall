NFTABLES_INIT = { "nftables": [
                    { "flush": { "ruleset": None } },
                    { "add": { "table": {
                        "family": "ip",
                        "name": "filter"
                    }}},
                    { "add": { "chain": {
                        "family": "ip",
                        "table": "filter",
                        "name": "INPUT"
                    }}},
                        { "add": { "chain": {
                        "family": "ip",
                        "table": "filter",
                        "name": "OUTPUT"
                    }}},
                        { "add": { "chain": {
                        "family": "ip",
                        "table": "filter",
                        "name": "FORWARD"
                    }}}
                ]}

NFTABLES_ADD_RULE = { "nftables": [
                        { "add": { "rule": {
                            "family": "ip",
                            "table": "filter",
                            "chain": "INPUT",
                            "expr": [
                                { "match": {
                                    "op": "==",
                                    "left": { "payload": {
										"protocol": "tcp",
                                        "field": "dport"
                                    }}
                                    ,
                                    "right": 10
                                }},
                                { 
                                    "accept": None 
                                }
                            ]
                        }}},
						{ "add": { "rule": {
                            "family": "ip",
                            "table": "filter",
                            "chain": "INPUT",
                            "expr": [
                                { "match": {
                                    "op": "==",
                                    "left": { "payload": {
										"protocol": "udp",
                                        "field": "dport"
                                    }},
                                    "right": 10
                                }},
                                { 
                                    "accept": None 
                                }
                            ]
                        }}}
                    ]}

NFTABLES_LIST_CHAIN = { "nftables": [
                        { "list": { "chain": {
							"family": "ip",
							"table": "filter",
							"name": "INPUT"
						}}}
                    ]}